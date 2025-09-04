from django.test import TestCase
from Blog.utils.dw_pvm_abilities import (
    apply_frenesie, apply_peau_dure_defense, apply_inspiration_heroique,
    apply_boureau, apply_mort_vivant, get_dino_abilities
)
from Blog.utils.dw_pvm_battle_logic import Dino, DinoStats, Attack, GameState


class PvMAbilitiesTestCase(TestCase):
    """Test cases for the new PvM abilities"""

    def setUp(self):
        """Set up test fixtures"""
        self.dino1 = Dino(
            id=1,
            name="TestDino1",
            user="test_user",
            stats=DinoStats(
                hp=1000,
                atk=100,
                defense=50,
                speed=1.0,
                crit_chance=0.1,
                crit_damage=1.5
            ),
            attack=Attack(
                name="test_attack",
                dmg_multiplier=(0.8, 1.2)
            )
        )
        
        self.dino2 = Dino(
            id=2,
            name="TestDino2",
            user="test_user",
            stats=DinoStats(
                hp=1000,
                atk=100,
                defense=50,
                speed=1.0,
                crit_chance=0.1,
                crit_damage=1.5
            ),
            attack=Attack(
                name="test_attack",
                dmg_multiplier=(0.8, 1.2)
            )
        )
        
        self.game_state = GameState(("Team1", [self.dino1]), ("Team2", [self.dino2]))

    def test_frenesie_ability(self):
        """Test that Frénésie increases speed when HP < 30%"""
        original_speed = self.dino1.stats.speed
        self.dino1.current_hp = 250  # 25% of 1000
        
        apply_frenesie(self.dino1, self.game_state)
        
        self.assertIn("frenesie", self.dino1.current_statuses)
        self.assertGreater(self.dino1.stats.speed, original_speed)

    def test_peau_dure_ability(self):
        """Test that Peau dure reduces damage when HP > 70%"""
        self.dino1.current_hp = 800  # 80% of 1000
        damage = 100
        
        reduced_damage = apply_peau_dure_defense(self.dino1, damage, self.game_state)
        
        self.assertEqual(reduced_damage, 85)  # 15% reduction

    def test_peau_dure_no_effect_low_hp(self):
        """Test that Peau dure doesn't reduce damage when HP <= 70%"""
        self.dino1.current_hp = 600  # 60% of 1000
        damage = 100
        
        normal_damage = apply_peau_dure_defense(self.dino1, damage, self.game_state)
        
        self.assertEqual(normal_damage, 100)  # No reduction

    def test_boureau_ability(self):
        """Test that Boureau executes target when conditions are met"""
        self.dino2.current_hp = 50
        damage = 80
        
        apply_boureau(self.dino1, self.dino2, damage, self.game_state)
        
        self.assertEqual(self.dino2.current_hp, 0)

    def test_inspiration_heroique_ability(self):
        """Test that Inspiration héroïque increases team attack"""
        team = [self.dino1, self.dino2]
        original_atk1 = self.dino1.stats.atk
        original_atk2 = self.dino2.stats.atk
        
        apply_inspiration_heroique(self.dino1, team, self.game_state)
        
        self.assertGreater(self.dino1.stats.atk, original_atk1)
        self.assertGreater(self.dino2.stats.atk, original_atk2)

    def test_mort_vivant_ability(self):
        """Test that Mort-vivant makes dino continue fighting after death"""
        team = [self.dino1, self.dino2]  # Has teammates
        self.dino1.current_hp = 0
        
        apply_mort_vivant(self.dino1, team, self.game_state)
        
        self.assertIn("mort_vivant", self.dino1.current_statuses)
        self.assertIn("untargetable", self.dino1.current_statuses)
        self.assertTrue(self.dino1.is_alive())  # Should be considered alive

    def test_mort_vivant_last_dino(self):
        """Test that Mort-vivant doesn't activate if it's the last dino"""
        team = [self.dino1]  # Only one dino
        self.dino1.current_hp = 0
        
        apply_mort_vivant(self.dino1, team, self.game_state)
        
        self.assertNotIn("mort_vivant", self.dino1.current_statuses)


# Create your tests here.
