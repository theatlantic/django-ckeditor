__version_info__ = (3, 6, 3)
__atl_version_info__ = (1, 12)
__version__ = '%s-atl-%s' % tuple(
    ['.'.join(map(str, v)) for v in [__version_info__, __atl_version_info__]])
