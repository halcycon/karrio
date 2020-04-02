from typing import Dict, Any
import pkgutil
import purplship.extension.mappers as extensions

Providers: Dict[str, Any] = {}

try:
    import purplship.package.mappers.aups as aups
    Providers.update({'aups': aups})
except ImportError:
    pass
try:
    import purplship.package.mappers.caps as caps
    Providers.update({'caps': caps})
except ImportError:
    pass
try:
    import purplship.package.mappers.dhl as dhl
    Providers.update({'dhl': dhl})
except ImportError:
    pass
try:
    import purplship.package.mappers.fedex as fedex
    Providers.update({'fedex': fedex})
except ImportError:
    pass
try:
    import purplship.package.mappers.purolator as purolator
    Providers.update({'purolator': purolator})
except ImportError:
    pass
try:
    import purplship.package.mappers.ups as ups
    Providers.update({'ups': ups})
except ImportError:
    pass
try:
    import purplship.package.mappers.usps as usps
    Providers.update({'usps': usps})
except ImportError:
    pass
try:
    import purplship.package.mappers.sendle as sendle
    Providers.update({'sendle': sendle})
except ImportError:
    pass


for _, name, _ in pkgutil.iter_modules(extensions.__path__):
    Providers.update({name: __import__(f'{extensions.__name__}.{name}', fromlist=[name])})