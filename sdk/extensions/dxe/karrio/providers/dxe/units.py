
import karrio.lib as lib
import karrio.core.units as units


class PackagingType(lib.Flag):
    """ Carrier specific packaging type """
    PACKAGE = "PACKAGE"

    """ Unified Packaging type mapping """
    envelope = PACKAGE
    pak = PACKAGE
    tube = PACKAGE
    pallet = PACKAGE
    small_box = PACKAGE
    medium_box = PACKAGE
    your_packaging = PACKAGE


class ShippingService(lib.Enum):
    """ Carrier specific services """
    dxe_standard_service = "DX Express Standard Service"


class ShippingOption(lib.Enum):
    """ Carrier specific options """
    # dxe_option = lib.OptionEnum("code")

    """ Unified Option type mapping """
    # insurance = dxe_coverage  #  maps unified karrio option to carrier specific

    pass


def shipping_options_initializer(
    options: dict,
    package_options: units.ShippingOptions = None,
) -> units.ShippingOptions:
    """
    Apply default values to the given options.
    """

    if package_options is not None:
        options.update(package_options.content)

    def items_filter(key: str) -> bool:
        return key in ShippingOption  # type: ignore

    return units.ShippingOptions(options, ShippingOption, items_filter=items_filter)
