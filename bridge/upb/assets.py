from bridge.model.attributes import  Attributes, BinaryAttribute, IntegerAttribute, ASCIIAttribute, ByteAttribute
from bridge.model.assets.basic_assets import OnOffAsset

class GenericUPBAsset(OnOffAsset):
    def __init__(self, name, real_id, service):
        super().__init__(name, real_id, service, "Generic UPB Device")
        self.attributes.add(
                IntegerAttribute("Level", 0, 101),
                ByteAttribute("Network ID"),
                ByteAttribute("Unit ID"),
                ASCIIAttribute("Network Password", 4),
                ByteAttribute("UBP Options"),
                ByteAttribute("UPB Version"),
                IntegerAttribute("Manufacture ID", 0, 65536),
                IntegerAttribute("Product ID", 0, 65536),
                IntegerAttribute("Firmware Version", 0, 65536),
                IntegerAttribute("Serial Number", 0, 4294967296),
                ASCIIAttribute("Network Name", 16),
                ASCIIAttribute("Room Name", 16),
                ASCIIAttribute("Device Name", 16))
