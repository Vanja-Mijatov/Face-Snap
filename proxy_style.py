from PyQt5.QtWidgets import QProxyStyle, QStyle


class MyProxyStyle(QProxyStyle):
    """
    Represents proxy style for main window and extends QProxyStyle
    """
    pass

    def pixelMetric(self, style_pixel_metric, option=None, widget=None):
        """Applies custom metric to button icons.

        :param self: self
        :param style_pixel_metric: type of element
        :param option: metric options
        :param widget: widget containing element
        :returns: metric for element
        """
        if style_pixel_metric == QStyle.PM_ButtonIconSize:
            return 200
        else:
            return QProxyStyle.pixelMetric(self, style_pixel_metric, option, widget)