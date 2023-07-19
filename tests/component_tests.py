import unittest

from necrotopia.Component import Component, ComponentFactory
from necrotopia.models import Grade

ALLOY_METAL = "Alloy Metal"
MACHINED_COMPONENTS = "Machined Components"
MECHANICAL_COMPONENTS = "Mechanical Components"
HARD_METAL = "Hard Metal"
RECOVERED_ELECTRONICS = "Recovered Electronics"

BASIC_SCRAP = "Basic Scrap"
UNCOMMON_SCRAP = "Uncommon Scrap"
RARE_SCRAP = "Rare Scrap"

MECHANICAL_AUTO_FRAME = "Mechanical Auto Frame"
MECHANICAL_ENGINE = "Mechanical Engine"
MECHANICAL_GEAR_SYSTEM = "Mechanical Gear System"

GLITTER_GULCH_RAIDER_RIDE = "Glitter Gulch Raider Ride"
class HelperFactory:

    @staticmethod
    def get_basic_frame() -> Component:
        result = ComponentFactory.create(name=MECHANICAL_AUTO_FRAME, quantity=1, mind=5, time=20, grade=Grade.Basic)
        result.add(ComponentFactory.create(name=ALLOY_METAL, quantity=3))
        result.add(ComponentFactory.create(name=MACHINED_COMPONENTS, quantity=2))
        result.add(ComponentFactory.create(name=RECOVERED_ELECTRONICS, quantity=2))

        return result
    @staticmethod
    def get_proficient_frame() -> Component:
        basic_frame = HelperFactory.get_basic_frame()
        result = ComponentFactory.create(name=MECHANICAL_AUTO_FRAME, quantity=1, mind=10, time=20, grade=Grade.Proficient)
        result.add(ComponentFactory.create(name=ALLOY_METAL, quantity=1))
        result.add(ComponentFactory.create(name=MACHINED_COMPONENTS, quantity=1))
        result.add(ComponentFactory.create(name=RECOVERED_ELECTRONICS, quantity=1))
        result.add(basic_frame)

        return result

    @staticmethod
    def get_master_frame() -> Component:
        proficient_frame = HelperFactory.get_proficient_frame()
        result = ComponentFactory.create(name=MECHANICAL_AUTO_FRAME, quantity=1, mind=15, time=20, grade=Grade.Master)
        result.add(ComponentFactory.create(name=ALLOY_METAL, quantity=1))
        result.add(ComponentFactory.create(name=MACHINED_COMPONENTS, quantity=1))
        result.add(ComponentFactory.create(name=RECOVERED_ELECTRONICS, quantity=1))

        result.add(proficient_frame)

        return result

    @staticmethod
    def get_basic_engine():
        result = ComponentFactory.create(name=MECHANICAL_ENGINE, quantity=1, mind=5, time=20, grade=Grade.Basic)
        result.add(ComponentFactory.create(name=HARD_METAL, quantity=3))
        result.add(ComponentFactory.create(name=MACHINED_COMPONENTS, quantity=1))
        result.add(ComponentFactory.create(name=MECHANICAL_COMPONENTS, quantity=1))


        return result

    @staticmethod
    def get_proficient_engine():
        result = ComponentFactory.create(name=MECHANICAL_ENGINE, quantity=1, mind=10, time=20, grade=Grade.Proficient)
        result.add(ComponentFactory.create(name=HARD_METAL, quantity=2))
        result.add(ComponentFactory.create(name=MACHINED_COMPONENTS, quantity=1))
        result.add(ComponentFactory.create(name=MECHANICAL_COMPONENTS, quantity=1))
        result.add(HelperFactory.get_basic_engine())

        return result

    @staticmethod
    def get_master_engine():
        result = ComponentFactory.create(name=MECHANICAL_ENGINE, quantity=1, mind=15, time=20, grade=Grade.Master)
        result.add(ComponentFactory.create(name=HARD_METAL, quantity=2))
        result.add(ComponentFactory.create(name=MACHINED_COMPONENTS, quantity=1))
        result.add(ComponentFactory.create(name=MECHANICAL_COMPONENTS, quantity=1))
        result.add(HelperFactory.get_proficient_engine())

        return result

    @staticmethod
    def get_basic_gears():
        result = ComponentFactory.create(name=MECHANICAL_GEAR_SYSTEM, quantity=1, mind=5, time=20, grade=Grade.Basic)
        result.add(ComponentFactory.create(name=MACHINED_COMPONENTS, quantity=3))
        result.add(ComponentFactory.create(name=ALLOY_METAL, quantity=1))
        result.add(ComponentFactory.create(name=HARD_METAL, quantity=1))

        return result

    @staticmethod
    def get_proficient_gears():
        result = ComponentFactory.create(name=MECHANICAL_GEAR_SYSTEM, quantity=1, mind=10, time=20, grade=Grade.Proficient)
        result.add(ComponentFactory.create(name=MACHINED_COMPONENTS, quantity=2))
        result.add(ComponentFactory.create(name=ALLOY_METAL, quantity=1))
        result.add(ComponentFactory.create(name=HARD_METAL, quantity=1))
        result.add(HelperFactory.get_basic_gears())

        return result

    @staticmethod
    def get_master_gears():
        result = ComponentFactory.create(name=MECHANICAL_GEAR_SYSTEM, quantity=1, mind=15, time=20, grade=Grade.Master)
        result.add(ComponentFactory.create(name=MACHINED_COMPONENTS, quantity=2))
        result.add(ComponentFactory.create(name=ALLOY_METAL, quantity=1))
        result.add(ComponentFactory.create(name=HARD_METAL, quantity=1))
        result.add(HelperFactory.get_proficient_gears())

        return result

    @classmethod
    def get_basic_raider_ride(cls):
        result = ComponentFactory.create(name=GLITTER_GULCH_RAIDER_RIDE, quantity=1, mind=5, time=20, grade=Grade.Basic)
        result.add(HelperFactory.get_basic_frame())
        result.add(HelperFactory.get_basic_engine())
        result.add(HelperFactory.get_basic_gears())
        result.add(ComponentFactory.create(name=BASIC_SCRAP, quantity=5))

        return result

    @classmethod
    def get_proficient_raider_ride(cls):
        basic_raider_ride = HelperFactory.get_basic_raider_ride()

        result = ComponentFactory.create(name=GLITTER_GULCH_RAIDER_RIDE, quantity=1, mind=10, time=20, grade=Grade.Proficient)
        result.add(HelperFactory.get_proficient_frame())
        result.add(HelperFactory.get_proficient_engine())
        result.add(HelperFactory.get_proficient_gears())
        result.add(ComponentFactory.create(name=UNCOMMON_SCRAP, quantity=5))
        result.add(basic_raider_ride)

        return result

    @classmethod
    def get_master_raider_ride(cls):
        proficient_raider_ride = HelperFactory.get_proficient_raider_ride()

        result = ComponentFactory.create(name=GLITTER_GULCH_RAIDER_RIDE, quantity=1, mind=15, time=20, grade=Grade.Master)
        result.add(HelperFactory.get_master_frame())
        result.add(HelperFactory.get_master_engine())
        result.add(HelperFactory.get_master_gears())
        result.add(ComponentFactory.create(name=RARE_SCRAP, quantity=5))
        result.add(proficient_raider_ride)

        return result


class ComponentTests(unittest.TestCase):
    def test_frames(self):
        basic_frame = HelperFactory.get_basic_frame()
        self.assertEqual(basic_frame.get_total_mind(), 5)
        self.assertEqual(basic_frame.get_total_time(), 20)

        proficient_frame = HelperFactory.get_proficient_frame()
        self.assertEqual(proficient_frame.get_total_mind(), 15)
        self.assertEqual(proficient_frame.get_total_time(), 40)

        master_frame = HelperFactory.get_master_frame()
        self.assertEqual(master_frame.get_total_mind(), 30)
        self.assertEqual(master_frame.get_total_time(), 60)

    def test_engines(self):
        basic_engine = HelperFactory.get_basic_engine()
        self.assertEqual(basic_engine.get_total_mind(), 5)
        self.assertEqual(basic_engine.get_total_time(), 20)

        proficient_engine = HelperFactory.get_proficient_engine()
        self.assertEqual(proficient_engine.get_total_mind(), 15)
        self.assertEqual(proficient_engine.get_total_time(), 40)

        master_engine = HelperFactory.get_master_engine()
        self.assertEqual(master_engine.get_total_mind(), 30)
        self.assertEqual(master_engine.get_total_time(), 60)

    def test_gears(self):
        basic_gears = HelperFactory.get_basic_gears()
        self.assertEqual(basic_gears.get_total_mind(), 5)
        self.assertEqual(basic_gears.get_total_time(), 20)

        proficient_gears = HelperFactory.get_proficient_gears()
        self.assertEqual(proficient_gears.get_total_mind(), 15)
        self.assertEqual(proficient_gears.get_total_time(), 40)

        master_gears = HelperFactory.get_master_gears()
        self.assertEqual(master_gears.get_total_mind(), 30)
        self.assertEqual(master_gears.get_total_time(), 60)

    def test_rides(self):
        basic_raider_ride = HelperFactory.get_basic_raider_ride()
        self.assertEqual(basic_raider_ride.get_total_mind(), 20)
        self.assertEqual(basic_raider_ride.get_total_time(), 80)

        proficient_raider_ride = HelperFactory.get_proficient_raider_ride()
        self.assertEqual(proficient_raider_ride.get_total_mind(), 75)
        self.assertEqual(proficient_raider_ride.get_total_time(), 220)

        master_raider_ride = HelperFactory.get_master_raider_ride()
        self.assertEqual(master_raider_ride.get_total_mind(), 180)
        self.assertEqual(master_raider_ride.get_total_time(), 420)

    def test_basic_collapse(self):
        basic_raider_ride = HelperFactory.get_basic_raider_ride()
        resources = basic_raider_ride.collapse()

        alloy_metal = resources[ALLOY_METAL]
        self.assertEqual(alloy_metal, 4)

        basic_scrap = resources[BASIC_SCRAP]
        self.assertEqual(basic_scrap, 5)

        machined_components = resources[MACHINED_COMPONENTS]
        self.assertEqual(machined_components, 6)

        mechanical_components = resources[MECHANICAL_COMPONENTS]
        self.assertEqual(mechanical_components, 1)

    def test_proficient_collapse(self):
        proficient_raider_ride = HelperFactory.get_proficient_raider_ride()
        resources = proficient_raider_ride.collapse()

        basic_scrap = resources[BASIC_SCRAP]
        self.assertEqual(basic_scrap, 5)

        uncommon_scrap = resources[UNCOMMON_SCRAP]
        self.assertEqual(uncommon_scrap, 5)

        hard_metal = resources[HARD_METAL]
        self.assertEqual(hard_metal, 11)

        alloy_metal = resources[ALLOY_METAL]
        self.assertEqual(alloy_metal, 10)

        machined_components = resources[MACHINED_COMPONENTS]
        self.assertEqual(machined_components, 16)

        mechanical_components = resources[MECHANICAL_COMPONENTS]
        self.assertEqual(mechanical_components, 3)

        recovered_electronics = resources[RECOVERED_ELECTRONICS]
        self.assertEqual(recovered_electronics, 5)

    def test_master_collapse(self):
        master_raider_ride = HelperFactory.get_master_raider_ride()
        resources = master_raider_ride.collapse()

        basic_scrap = resources[BASIC_SCRAP]
        self.assertEqual(basic_scrap, 5)

        uncommon_scrap = resources[UNCOMMON_SCRAP]
        self.assertEqual(uncommon_scrap, 5)

        rare_scrap = resources[RARE_SCRAP]
        self.assertEqual(rare_scrap, 5)

        hard_metal = resources[HARD_METAL]
        self.assertEqual(hard_metal, 21)

        alloy_metal = resources[ALLOY_METAL]
        self.assertEqual(alloy_metal, 18)

        machined_components = resources[MACHINED_COMPONENTS]
        self.assertEqual(machined_components, 30)

        mechanical_components = resources[MECHANICAL_COMPONENTS]
        self.assertEqual(mechanical_components, 6)

        recovered_electronics = resources[RECOVERED_ELECTRONICS]
        self.assertEqual(recovered_electronics, 9)

        mind = master_raider_ride.get_total_mind()
        time = master_raider_ride.get_total_time()


if __name__ == '__main__':
    unittest.main()
