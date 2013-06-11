from bridge.model.attributes import  Attributes, BinaryAttribute, IntegerAttribute, ASCIIAttribute, ByteAttribute
from bridge.model.assets.basic_assets import OnOffAsset

class GenericUPBAsset(OnOffAsset):
    def __init__(self, name, real_id, service):
        super().__init__(name, real_id, service, "Generic UPB Device")
        self.attributes.add(
                IntegerAttribute('level', 0, 101),
                ByteAttribute('nid'),
                ByteAttribute('uid'),
                ASCIIAttribute('npw', 4),
                ByteAttribute('ubop'),
                ByteAttribute('upbver'),
                IntegerAttribute('mid', 0, 65536),
                IntegerAttribute('pid', 0, 65536),
                IntegerAttribute('fwver', 0, 65536),
                IntegerAttribute('sernum', 0, 4294967296),
                ASCIIAttribute('nname', 16),
                ASCIIAttribute('rname', 16),
                ASCIIAttribute('dname', 16))
