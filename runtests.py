import os
import sys
import argparse
import time
import traceback
import unittest
from distutils import log

import pep8
from six import StringIO

from coverage import coverage, misc
from setuptools.command.test import test as TestCommand


class LabelException(Exception):
    pass


class test(TestCommand):
    user_options = TestCommand.user_options + [
        ('autoreload', 'a', "Test suite will restart when code changes are detected."),
        ('failfast', 'f', "Test suite will stop running after the first test failure is detected."),
        ('label=', 'l', "Only run tests for specified label. Label should be of the form app.TestClass or app.TestClass.test_method."),
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.test_suite = 'setuptest.setuptest.SetupTestSuite'
        self.autoreload = 0
        self.failfast = 0
        self.label = 0

    def run_tests(self):
        auto_reload = False
        if '-a' in sys.argv or '--autoreload' in sys.argv:
            auto_reload = True
        
        if auto_reload:
            from django.utils.autoreload import restart_with_reloader, reloader_thread
            if os.environ.get("RUN_MAIN") == "true":
                try:
                    TestCommand.run_tests(self)
                except LabelException:
                    sys.exit(1)
                except:
                    pass
                try:
                    reloader_thread()
                except KeyboardInterrupt:
                    pass
            else:
                try:
                    sys.exit(restart_with_reloader())
                except KeyboardInterrupt:
                    pass
        else:
            return TestCommand.run_tests(self)


class SetupTestSuite(unittest.TestSuite):
    """
    Test Suite configuring Django settings and using
    DiscoverRunner or DjangoTestSuiteRunner as the test runner.
    Also runs PEP8 and Coverage checks.
    """
    def __init__(self, *args, **kwargs):
        self.cov = coverage()
        self.cov.start()
        self.configure()
        self.packages = self.resolve_packages()

        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--autoreload', dest='autoreload',
                action='store_const', const=True, default=False,)
        parser.add_argument('-f', '--failfast', dest='failfast',
                action='store_const', const=True, default=False,)
        parser.add_argument('-l', '--label', dest='label')
        self.options = vars(parser.parse_args(sys.argv[2:]))
        sys.argv = sys.argv[:2]

        runner_options = {
            'verbosity': 1,
            'interactive': True,
            'failfast': False,
        }

        from django.test.runner import DiscoverRunner
        self.test_runner = DiscoverRunner(**runner_options)
        tests = self.test_runner.build_suite()

        super(SetupTestSuite, self).__init__(tests=tests, *args, **kwargs)
        self.test_runner.setup_test_environment()
        self.old_config = self.test_runner.setup_databases()

    def handle_label_exception(self, exception):
        """
        Check whether or not the exception was caused due to a bad label
        being provided. If so raise LabelException which will cause an exit,
        otherwise continue.

        The check looks for particular error messages, which obviously sucks.
        TODO: Implement a cleaner test.
        """
        markers = [
            'no such test method',
            'should be of the form app.TestCase or app.TestCase.test_method',
            'App with label',
            'does not refer to a test',
        ]
        if any(marker in exception.message for marker in markers):
            log.info(exception)
            raise LabelException(exception)
        else:
            raise exception

    def build_tests(self):
        """
        Build tests for inclusion in suite from resolved packages for <= 1.8
        TODO: Cleanup/simplify this method, flow too complex,
        too much duplication.
        """
        from django.core.exceptions import ImproperlyConfigured
        from django.test.simple import build_suite, build_test
        from django.apps import apps
        get_app = apps.get_app_config

        tests = []
        packages = [self.options['label'], ] if self.options['label'] else self.packages
        for package in packages:
            try:
                if not self.options['autoreload']:
                    if self.options['label']:
                        try:
                            tests.append(build_test(package))
                        except (ImproperlyConfigured, ValueError) as e:
                            self.handle_label_exception(e)
                    else:
                        app = get_app(package)
                        tests.append(build_suite(app))
                else:
                    # Wait for exceptions to be resolved.
                    exception = None
                    while True:
                        try:
                            if self.options['label']:
                                try:
                                    tests.append(build_test(package))
                                except (ImproperlyConfigured, ValueError) as e:
                                    self.handle_label_exception(e)
                            else:
                                app = get_app(package)
                                tests.append(build_suite(app))
                            break
                        except LabelException:
                            raise
                        except Exception as e:
                            if exception != str(e):
                                traceback.print_exc()
                            exception = str(e)
                            time.sleep(1)
            except ImproperlyConfigured as e:
                log.info("Warning: %s" % traceback.format_exc())
            except ImportError as e:
                log.info("Warning: %s" % traceback.format_exc())

        return tests

    def configure(self):
        """
        Configures Django settings.
        """

        import django
        from django.conf import settings
        try:
            from django.utils.importlib import import_module
        except ImportError:
            from importlib import import_module
        try:
            test_settings = import_module('test_settings')
        except ImportError as e:
            log.info('ImportError: Unable to import test settings: %s' % e)
            sys.exit(1)

        setting_attrs = {}
        for attr in dir(test_settings):
            if '__' not in attr:
                setting_attrs[attr] = getattr(test_settings, attr)

        if not settings.configured:
            settings.configure(**setting_attrs)

        if hasattr(django, 'setup'):
            django.setup()

    def coverage_report(self):
        """
        Outputs Coverage report to screen and coverage.xml.
        """
        verbose = '--quiet' not in sys.argv
        self.cov.stop()
        if verbose:
            log.info("\nCoverage Report:")
            try:
                include = ['%s*' % package for package in self.packages]
                omit = ['*tests*']
                self.cov.report(include=include, omit=omit)
                self.cov.save()
                self.cov.xml_report(include=include, omit=omit)
            except misc.CoverageException as e:
                log.info("Coverage Exception: %s" % e)

    def resolve_packages(self):
        """
        Frame hack to determine packages contained in module for testing.
        We ignore submodules (those containing '.')
        """
        f = sys._getframe()
        while f:
            if 'self' in f.f_locals:
                locals_self = f.f_locals['self']
                py_modules = getattr(locals_self, 'py_modules', None)
                packages = getattr(locals_self, 'packages', None)

                top_packages = []
                if py_modules or packages:
                    if py_modules:
                        for module in py_modules:
                            if '.' not in module:
                                top_packages.append(module)
                    if packages:
                        for package in packages:
                            if '.' not in package:
                                top_packages.append(package)

                    return list(set(top_packages))
            f = f.f_back

    def pep8_report(self):
        """
        Outputs PEP8 report to screen and pep8.txt.
        """
        verbose = '--quiet' not in sys.argv
        if verbose:
            # Hook into stdout.
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()

            # Run Pep8 checks, excluding South migrations.
            pep8_style = pep8.StyleGuide()
            pep8_style.options.exclude.append('migrations')
            pep8_style.options.exclude.append('south_migrations')
            pep8_style.check_files(self.packages)

            # Restore stdout.
            sys.stdout = old_stdout

            # Save result to pep8.txt.
            result = mystdout.getvalue()
            output = open('pep8.txt', 'w')
            output.write(result)
            output.close()

            # Return Pep8 result
            if result:
                log.info("\nPEP8 Report:")
                log.info(result)

    def run(self, result, *args, **kwargs):
        """
        Run the test, teardown the environment and generate reports.
        """
        result.failfast = self.options['failfast']
        result = super(SetupTestSuite, self).run(result, *args, **kwargs)
        self.test_runner.teardown_databases(self.old_config)
        self.test_runner.teardown_test_environment()
        self.coverage_report()
        self.pep8_report()
        return result
