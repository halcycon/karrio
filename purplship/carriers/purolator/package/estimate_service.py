from typing import List, Tuple, cast
from datetime import datetime
from pysoap.envelope import Envelope
from pypurolator.estimate_service import (
    GetFullEstimateRequest, Shipment, SenderInformation, Address, ReceiverInformation,
    PackageInformation, TrackingReferenceInformation, PickupInformation,
    ArrayOfPiece, Piece, Weight as PurolatorWeight, WeightUnit as PurolatorWeightUnit, RequestContext,
    Dimension as PurolatorDimension, DimensionUnit as PurolatorDimensionUnit, TotalWeight,
    ShipmentEstimate, Tax, Surcharge, OptionPrice, PickupType, PhoneNumber
)
from purplship.core.units import Currency, Package
from purplship.core.utils import Serializable, Element, concat_str, format_date, decimal
from purplship.core.utils.soap import create_envelope
from purplship.core.errors import RequiredFieldError
from purplship.core.models import RateRequest, RateDetails, Message, ChargeDetails
from purplship.carriers.purolator.utils import Settings, standard_request_serializer
from purplship.carriers.purolator.error import parse_error_response
from purplship.carriers.purolator.units import Product, PackagePresets


def parse_full_estimate_response(response: Element, settings: Settings) -> Tuple[List[RateDetails], List[Message]]:
    estimates = response.xpath(".//*[local-name() = $name]", name="ShipmentEstimate")
    return (
        [_extract_rate(node, settings) for node in estimates],
        parse_error_response(response, settings)
    )


def _extract_rate(estimate_node: Element, settings: Settings) -> RateDetails:
    estimate = ShipmentEstimate()
    estimate.build(estimate_node)
    currency = Currency.CAD.name
    duties_and_taxes = [
        ChargeDetails(
            name=cast(Tax, tax).Description,
            amount=decimal(cast(Tax, tax).Amount),
            currency=currency
        ) for tax in estimate.Taxes.Tax
    ]
    surcharges = [
        ChargeDetails(
            name=cast(Surcharge, charge).Description,
            amount=decimal(cast(Surcharge, charge).Amount),
            currency=currency
        ) for charge in estimate.Surcharges.Surcharge
    ]
    option_charges = [
        ChargeDetails(
            name=cast(OptionPrice, charge).Description,
            amount=decimal(cast(OptionPrice, charge).Amount),
            currency=currency
        ) for charge in estimate.OptionPrices.OptionPrice
    ]
    service = next((p.name for p in Product if p.value in estimate.ServiceID), estimate.ServiceID)
    return RateDetails(
        carrier=settings.carrier,
        carrier_name=settings.carrier_name,
        service=service,
        currency=currency,
        base_charge=decimal(estimate.BasePrice),
        estimated_delivery=format_date(estimate.ExpectedDeliveryDate),
        total_charge=decimal(estimate.TotalPrice),
        duties_and_taxes=decimal(sum(c.amount for c in duties_and_taxes)),
        extra_charges=(duties_and_taxes + surcharges + option_charges)
    )


def get_full_estimate_request(payload: RateRequest, settings: Settings) -> Serializable[Envelope]:
    parcel_preset = PackagePresets[payload.parcel.package_preset].value if payload.parcel.package_preset else None
    package = Package(payload.parcel, parcel_preset)

    if package.weight.value is None:
        raise RequiredFieldError("parcel.weight")

    service = next(
        (Product[s].value for s in payload.parcel.services if s in Product.__members__),
        Product.purolator_express.value
    )
    request = create_envelope(
        envelope_prefix="SOAP-ENV",
        header_prefix="ns1",
        header_content=RequestContext(
            Version='2.1',
            Language=settings.language,
            GroupID=None,
            RequestReference=None,
            UserToken=settings.user_token
        ),
        body_prefix="ns1",
        body_content=GetFullEstimateRequest(
            Shipment=Shipment(
                SenderInformation=SenderInformation(
                    Address=Address(
                        Name=payload.shipper.person_name,
                        Company=payload.shipper.company_name,
                        Department=None,
                        StreetNumber=None,
                        StreetSuffix=None,
                        StreetName=concat_str(payload.shipper.address_line1, join=True),
                        StreetType=None,
                        StreetDirection=None,
                        Suite=None,
                        Floor=None,
                        StreetAddress2=concat_str(payload.shipper.address_line2, join=True),
                        StreetAddress3=None,
                        City=payload.shipper.city,
                        Province=payload.shipper.state_code,
                        Country=payload.shipper.country_code,
                        PostalCode=payload.shipper.postal_code,
                        PhoneNumber=PhoneNumber(Phone=payload.shipper.phone_number),
                        FaxNumber=None
                    ),
                    TaxNumber=payload.shipper.federal_tax_id or payload.shipper.state_tax_id
                ),
                ReceiverInformation=ReceiverInformation(
                    Address=Address(
                        Name=payload.recipient.person_name,
                        Company=payload.recipient.company_name,
                        Department=None,
                        StreetNumber=None,
                        StreetSuffix=None,
                        StreetName=concat_str(payload.recipient.address_line1, join=True),
                        StreetType=None,
                        StreetDirection=None,
                        Suite=None,
                        Floor=None,
                        StreetAddress2=concat_str(payload.recipient.address_line2, join=True),
                        StreetAddress3=None,
                        City=payload.recipient.city,
                        Province=payload.recipient.state_code,
                        Country=payload.recipient.country_code,
                        PostalCode=payload.recipient.postal_code,
                        PhoneNumber=PhoneNumber(Phone=payload.recipient.phone_number),
                        FaxNumber=None
                    ),
                    TaxNumber=payload.recipient.federal_tax_id or payload.recipient.state_tax_id
                ),
                FromOnLabelIndicator=None,
                FromOnLabelInformation=None,
                ShipmentDate=datetime.today().strftime("%Y-%m-%d"),
                PackageInformation=PackageInformation(
                    ServiceID=service,
                    Description=payload.parcel.description,
                    TotalWeight=TotalWeight(
                        Value=package.weight.value,
                        WeightUnit=PurolatorWeightUnit[package.weight_unit.value].value
                    ) if payload.parcel.weight else None,
                    TotalPieces=1,
                    PiecesInformation=ArrayOfPiece(
                        Piece=[
                            Piece(
                                Weight=PurolatorWeight(
                                    Value=package.weight.value,
                                    WeightUnit=PurolatorWeightUnit[package.weight_unit.value].value
                                ) if payload.parcel.weight else None,
                                Length=PurolatorDimension(
                                    Value=package.length.value,
                                    DimensionUnit=PurolatorDimensionUnit[package.dimension_unit.value].value
                                ) if package.length.value else None,
                                Width=PurolatorDimension(
                                    Value=package.width.value,
                                    DimensionUnit=PurolatorDimensionUnit[package.dimension_unit.value].value
                                ) if package.width.value else None,
                                Height=PurolatorDimension(
                                    Value=package.height.value,
                                    DimensionUnit=PurolatorDimensionUnit[package.dimension_unit.value].value
                                ) if package.height.value else None,
                                Options=None
                            )
                        ]
                    ),
                    DangerousGoodsDeclarationDocumentIndicator=None,
                    OptionsInformation=None
                ),
                InternationalInformation=None,
                ReturnShipmentInformation=None,
                PaymentInformation=None,
                PickupInformation=PickupInformation(PickupType=PickupType.DROP_OFF.value),
                NotificationInformation=None,
                TrackingReferenceInformation=TrackingReferenceInformation(
                    Reference1=payload.parcel.reference,
                ),
                OtherInformation=None,
                ProactiveNotification=None
            ),
            ShowAlternativeServicesIndicator=True
        )
    )
    return Serializable(request, standard_request_serializer)