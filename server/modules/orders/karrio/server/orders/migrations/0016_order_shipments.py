# Generated by Django 4.1.7 on 2023-04-10 17:44

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Order = apps.get_model("orders", "Order")
    Shipment = apps.get_model("manager", "Shipment")
    orders = (
        Order.objects.using(db_alias)
        .filter(line_items__children__commodity_parcel__parcel_shipment__isnull=False)
        .iterator()
    )

    for _order in orders:
        shipments = (
            Shipment.objects.using(db_alias)
            .filter(
                pk__in=_order.line_items.all().values_list(
                    "children__commodity_parcel__parcel_shipment__pk", flat=True
                )
            )
            .distinct()
        )
        _order.shipments.add(*shipments)


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("manager", "0050_address_street_number_tracking_account_number_and_more"),
        ("orders", "0015_remove_order_order_id_idx_alter_order_order_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="shipments",
            field=models.ManyToManyField(
                related_name="shipment_order", to="manager.shipment"
            ),
        ),
        migrations.RunPython(forwards_func, reverse_func),
    ]
