from django.test import TestCase
from Blog.utils.dw_pvm_abilities import (
    apply_frenesie, apply_peau_dure_defense, apply_inspiration_heroique,
    apply_bourreau, apply_mort_vivant, get_dino_abilities, apply_vol_de_vie
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
        """Test that Frénésie increases speed when HP < 50%"""
        original_speed = self.dino1.stats.speed
        self.dino1.current_hp = 400  # 40% of 1000
        
        apply_frenesie(self.dino1, self.game_state)
        
        self.assertIn("frenesie", self.dino1.current_statuses)
        self.assertGreater(self.dino1.stats.speed, original_speed)

    def test_peau_dure_ability(self):
        """Test that Peau dure reduces damage when HP > 50%"""
        self.dino1.current_hp = 600  # 60% of 1000
        damage = 100
        
        reduced_damage = apply_peau_dure_defense(self.dino1, damage, self.game_state)
        
        self.assertEqual(reduced_damage, 80)  # 20% reduction

    def test_peau_dure_no_effect_low_hp(self):
        """Test that Peau dure doesn't reduce damage when HP <= 50%"""
        self.dino1.current_hp = 400  # 40% of 1000
        damage = 100
        
        normal_damage = apply_peau_dure_defense(self.dino1, damage, self.game_state)
        
        self.assertEqual(normal_damage, 100)  # No reduction

    def test_bourreau_ability(self):
        """Test that Bourreau has probability-based execution"""
        # Set target to very low HP for high execution chance
        self.dino2.current_hp = 10  # 1% of 1000, should have high execution chance
        damage = 50
        original_hp = self.dino2.current_hp
        
        # Run multiple times to test probability (at 1% HP, chance should be very high)
        executed = False
        for _ in range(10):  # Run 10 times to increase likelihood of execution
            self.dino2.current_hp = original_hp  # Reset HP
            apply_bourreau(self.dino1, self.dino2, damage, self.game_state)
            if self.dino2.current_hp == 0:
                executed = True
                break
        
        # With 1% HP, execution chance is (1-0.01^2)/1.1 ≈ 90.9%, should execute at least once in 10 attempts
        self.assertTrue(executed, "Bourreau should execute target with very low HP at least once in multiple attempts")

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
        """Test that Mort-vivant still activates for first death even if only one dino"""
        team = [self.dino1]  # Only one dino
        self.dino1.current_hp = 0
        
        apply_mort_vivant(self.dino1, team, self.game_state)
        
        # Should still activate since it's now a team ability for first death
        self.assertIn("mort_vivant", self.dino1.current_statuses)

    def test_vol_de_vie_ability(self):
        """Test that Vol de vie heals attacker for 30% of damage dealt"""
        self.dino1.current_hp = 500  # Reduced HP to test healing
        damage = 100
        original_hp = self.dino1.current_hp
        
        apply_vol_de_vie(self.dino1, damage, self.game_state)
        
        expected_heal = int(damage * 0.3)  # 30 HP
        self.assertEqual(self.dino1.current_hp, original_hp + expected_heal)

    def test_vol_de_vie_no_overheal(self):
        """Test that Vol de vie doesn't overheal beyond max HP"""
        self.dino1.current_hp = 990  # Near max HP
        damage = 100
        
        apply_vol_de_vie(self.dino1, damage, self.game_state)
        
        self.assertEqual(self.dino1.current_hp, self.dino1.stats.hp)  # Capped at max HP

    def test_vol_de_vie_no_damage(self):
        """Test that Vol de vie doesn't heal if no damage was dealt"""
        original_hp = self.dino1.current_hp
        damage = 0
        
        apply_vol_de_vie(self.dino1, damage, self.game_state)
        
        self.assertEqual(self.dino1.current_hp, original_hp)  # No healing

    # def test_provocation_target_selection(self):
    #     """Test that Provocation makes dino more likely to be targeted"""
    #     # This test is disabled due to import issues with battle logic functions
    #     pass


# Create your tests here.
