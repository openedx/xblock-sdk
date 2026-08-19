"""
Module contains various XBlock services for the workbench.
"""


from django.conf import settings


class SettingsService:
    """
    Allows server-wide configuration of XBlocks on a per-type basis.

    The service is copied as-is from the Open edX platform:

      - `edx-platform/common/lib/xmodule/xmodule/services.py`
    """
    xblock_settings_bucket_selector = 'block_settings_key'

    def get_settings_bucket(self, block, default=None):
        """ Gets xblock settings dictionary from settings. """
        if not block:
            raise ValueError("Expected XBlock instance, got {block} of type {type}".format(
                block=block,
                type=type(block)
            ))

        actual_default = default if default is not None else {}
        xblock_settings_bucket = getattr(block, self.xblock_settings_bucket_selector, block.unmixed_class.__name__)
        xblock_settings = settings.XBLOCK_SETTINGS if hasattr(settings, "XBLOCK_SETTINGS") else {}
        return xblock_settings.get(xblock_settings_bucket, actual_default)
