import graphene
from graphene_django.rest_framework.serializer_converter import (
    convert_serializer_to_input_type as serializer_to_input,
)

from purplship.server.core import serializers
from purplship.server.serializers import make_fields_optional, exclude_id_field
import purplship.server.graph.serializers as model_serializers
import purplship.server.graph.extension.base.types as types


def create_address_input(optional: bool = False) -> graphene.InputObjectType:
    _method = "Partial" if optional else ""
    _type = (
        make_fields_optional(model_serializers.AddressModelSerializer)
        if optional
        else exclude_id_field(model_serializers.AddressModelSerializer)
    )

    return type(
        f"{_method}Address",
        (serializer_to_input(_type),),
        dict(
            country_code=types.CountryCodeEnum(required=not optional),
        ),
    )


def create_commodity_input(optional: bool = False) -> graphene.InputObjectType:
    _method = "Partial" if optional else ""
    _type = (
        make_fields_optional(model_serializers.CommodityModelSerializer)
        if optional
        else exclude_id_field(model_serializers.CommodityModelSerializer)
    )

    return type(
        f"{_method}Commodity",
        (serializer_to_input(_type),),
        dict(
            parent_id=graphene.String(required=False),
            weight_unit=types.WeightUnitEnum(required=False),
            origin_country=types.CountryCodeEnum(required=False),
            value_currency=types.CurrencyCodeEnum(required=False),
            metadata=types.generic.GenericScalar(),
        ),
    )


def create_payment_input() -> graphene.InputObjectType:
    return type(
        "PartialPayment",
        (serializer_to_input(serializers.Payment),),
        dict(
            paid_by=types.PaidByEnum(required=False),
        ),
    )


def create_duty_input() -> graphene.InputObjectType:
    return type(
        "PartialDuty",
        (serializer_to_input(serializers.Duty),),
        dict(
            paid_by=types.PaidByEnum(required=False),
            currency=types.CurrencyCodeEnum(required=False),
            bill_to=graphene.Field(UpdateAddressInput, required=False),
        ),
    )


def create_customs_input(optional: bool = False) -> graphene.InputObjectType:
    _method = "Partial" if optional else ""
    _type = (
        make_fields_optional(model_serializers.CustomsModelSerializer)
        if optional
        else model_serializers.CustomsModelSerializer
    )

    return type(
        f"{_method}Customs",
        (serializer_to_input(_type),),
        dict(
            commodities=graphene.List(
                UpdateCommodityInput if optional else CreateCommodityInput
            ),
            incoterm=types.IncotermCodeEnum(required=False),
            content_type=types.CustomsContentTypeEnum(required=False),
            duty=graphene.Field(DutyInput, required=False),
            options=types.generic.GenericScalar(),
        ),
    )


def create_parcel_input(optional: bool = False) -> graphene.InputObjectType:
    _method = "Partial" if optional else ""
    _type = (
        make_fields_optional(model_serializers.ParcelModelSerializer)
        if optional
        else exclude_id_field(model_serializers.ParcelModelSerializer)
    )

    return type(
        f"{_method}Parcel",
        (serializer_to_input(_type),),
        dict(
            items=graphene.List(
                UpdateCommodityInput if optional else CreateCommodityInput
            ),
            weight_unit=types.WeightUnitEnum(required=False),
            dimension_unit=types.DimensionUnitEnum(required=False),
        ),
    )


def create_label_template_input(optional: bool = False) -> graphene.InputObjectType:
    _method = "Partial" if optional else ""
    _type = (
        make_fields_optional(model_serializers.LabelTemplateModelSerializer)
        if optional
        else exclude_id_field(model_serializers.LabelTemplateModelSerializer)
    )

    return type(
        f"{_method}LabelTemplate",
        (serializer_to_input(_type),),
        dict(
            template_type=types.LabelTypeEnum(required=False),
        ),
    )


def create_service_level_input(optional: bool = False) -> graphene.InputObjectType:
    _method = "Partial" if optional else ""
    _type = (
        make_fields_optional(model_serializers.ServiceLevelModelSerializer)
        if optional
        else exclude_id_field(model_serializers.ServiceLevelModelSerializer)
    )

    return type(
        f"{_method}ServiceLevel",
        (serializer_to_input(_type),),
        dict(
            weight_unit=types.WeightUnitEnum(required=False),
            dimension_unit=types.DimensionUnitEnum(required=False),
        ),
    )


def create_connection_input(optional: bool = False) -> graphene.InputObjectType:
    _method = "Update" if optional else "Create"
    _fields = dict()

    for name, serializer in model_serializers.CARRIER_MODEL_SERIALIZERS.items():
        _extra_fields = dict()
        _serializer = make_fields_optional(serializer) if optional else serializer

        if hasattr(_serializer.Meta.model, "label_template"):
            _extra_fields["label_template"] = graphene.Field(
                UpdateLabelTemplateInput if optional else CreateLabelTemplateInput,
                required=False,
            )

        if hasattr(_serializer.Meta.model, "services"):
            _extra_fields["services"] = graphene.List(
                UpdateServiceLevelInput if optional else CreateServiceLevelInput,
                required=False,
            )

        _input = type(
            f"{_method}{_serializer.__name__}",
            (serializer_to_input(_serializer),),
            _extra_fields,
        )
        _field = type(
            f"{_method}{serializer.__name__}",
            (_input,),
            dict(
                carrier_id=graphene.String(required=not optional),
                metadata=types.generic.GenericScalar(),
            ),
        )
        _fields.update(
            {
                name: graphene.Field(_field, required=False),
            }
        )

    return type("Settings", (object,), _fields)


PaymentInput = create_payment_input()
CreateCommodityInput = create_commodity_input()
UpdateCommodityInput = create_commodity_input(optional=True)
CreateAddressInput = create_address_input()
UpdateAddressInput = create_address_input(optional=True)
DutyInput = create_duty_input()
CreateCustomsInput = create_customs_input()
UpdateCustomsInput = create_customs_input(optional=True)
CreateParcelInput = create_parcel_input()
UpdateParcelInput = create_parcel_input(optional=True)

CreateAddressTemplateInput = type("CreateAddressTemplate", (CreateAddressInput,), {})
UpdateAddressTemplateInput = type("UpdateAddressTemplate", (UpdateAddressInput,), {})
CreateCustomsTemplateInput = type("CreateCustomsTemplate", (CreateCustomsInput,), {})
UpdateCustomsTemplateInput = type("UpdateCustomsTemplate", (UpdateCustomsInput,), {})
CreateParcelTemplateInput = type("CreateParcelTemplate", (CreateParcelInput,), {})
UpdateParcelTemplateInput = type("UpdateParcelTemplate", (UpdateParcelInput,), {})

CreateLabelTemplateInput = create_label_template_input()
UpdateLabelTemplateInput = create_label_template_input(optional=True)
CreateServiceLevelInput = create_service_level_input()
UpdateServiceLevelInput = create_service_level_input(optional=True)

CreateConnectionInput = create_connection_input()
UpdateConnectionInput = create_connection_input(optional=True)