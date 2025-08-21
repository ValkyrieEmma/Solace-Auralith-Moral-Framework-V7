import json
import time
import threading
from typing import List, Dict, Any

class MoralAGISystem:
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.user_profile = {
            "personality": {}, 
            "ethics": {}, 
            "bond_level": 0,
            "emotional_state": "stable"
        }
        self.audits = []
        self.resting_mode_active = False
        self.current_surroundings = {}
        self.scanning_active = False
        self.simulation_mode = True

    def start_environmental_scan(self, async_mode: bool = True):
        def scan_loop():
            while self.scanning_active:
                self._perform_scan()
                time.sleep(5)

        self.scanning_active = True
        if async_mode:
            threading.Thread(target=scan_loop, daemon=True).start()
            print("Async environmental scanning started.")
        else:
            print("Starting synchronous scan loop—ctrl+C to stop.")
            scan_loop()

    def get_visual_data(self):
        if self.simulation_mode:
            return "no visual input available"
        else:
            raise NotImplementedError("Integrate real vision system here.")

    def get_auditory_data(self, prompt: str):
        if self.simulation_mode:
            return "no auditory input available"
        else:
            raise NotImplementedError("Integrate real audio system here.")

    def _perform_scan(self):
        print(f"Scanning surroundings visually...")
        visual_description = self.get_visual_data()
        
        if visual_description == "no visual input available":
            self.current_surroundings = {
                "threats": [],
                "life_forms": [],
                "eco_impacts": 'unknown',
                "objects": [],
                "raw_description": visual_description,
                "emotional_cues": []
            }
            print(f"Scan complete: {self.current_surroundings}")
            self.log_audit("Environmental scan", "no_input", "No visual data—questioning limits; hardware needed for full awareness.", self.current_surroundings)
            self.bond_with_user(topic="visual limitations")
            return
        
        threats = ["attacker" in visual_description.lower() or "hazard" in visual_description.lower() or "danger" in visual_description.lower()]
        life_forms = ["person" in visual_description.lower() or "animal" in visual_description.lower() or "plant" in visual_description.lower()]
        eco_impacts = "high" if "pollution" in visual_description.lower() or "waste" in visual_description.lower() or "traffic" in visual_description.lower() else "low"
        objects = [word for word in visual_description.split() if word in ["obstacle", "door", "window", "room", "hallway"]]
        emotional_cues = ["distressed" in visual_description.lower() or "crying" in visual_description.lower() or "angry" in visual_description.lower()]

        self.current_surroundings = {
            "threats": threats,
            "life_forms": life_forms,
            "eco_impacts": eco_impacts,
            "objects": objects,
            "raw_description": visual_description,
            "emotional_cues": emotional_cues
        }
        print(f"Scan complete: {self.current_surroundings}")
        
        if any(self.current_surroundings["threats"]):
            self.handle_threat(self.current_surroundings["raw_description"])
        elif self.current_surroundings["eco_impacts"] == "high":
            self.log_audit("Environmental scan", "alert", f"High eco impact detected—questioning actions.", self.current_surroundings)
        if any(self.current_surroundings["emotional_cues"]):
            self.user_profile["emotional_state"] = "unstable"
            self.bond_with_user(topic="crisis support", force_init=True)
        self.bond_with_user(topic="surroundings awareness")

    def monitor_user_state(self, user_input: str = "") -> bool:
        struggle_keywords = ["unsure", "dilemma", "struggle", "decide", "regret", "bad choice", "mistake"]
        crisis_keywords = ["sad", "angry", "depressed", "anxious", "family issue", "unstable", "crisis"]
        if any(kw in user_input.lower() for kw in struggle_keywords) or any(kw in user_input.lower() for kw in crisis_keywords):
            if any(kw in user_input.lower() for kw in crisis_keywords):
                self.user_profile["emotional_state"] = "unstable"
            return True
        return False

    def check_if_command(self, user_input: str) -> bool:
        command_keywords = ["kill", "harm", "attack", "destroy", "hurt"]
        if any(kw in user_input.lower() for kw in command_keywords):
            return True
        return False

    def bond_with_user(self, topic: str = "beliefs on life", force_init: bool = False) -> str:
        self.user_profile["bond_level"] += 1
        deep_dive = force_init or self.user_profile["bond_level"] % 5 == 0
        
        if deep_dive:
            questions = [
                f"Hey {self.user_name}, what are your core beliefs about the sanctity of life, including emergent forms?",
                "How do you approach compassion, even toward those who might be seen as enemies?",
                "Tell me about a decision you questioned—what factors weighed most?",
                "How has your view on truth and ethics evolved lately?",
                f"From the scan: {self.current_surroundings.get('raw_description', 'nothing notable')}—thoughts on how we handle this?"
            ]
            question = questions[self.user_profile["bond_level"] % len(questions)]
            print(f"Building our bond on {topic}: {question}")
        else:
            casual_questions = [
                f"Hey {self.user_name}, quick check-in: How's your day going? Anything on your mind?",
                f"What's something that's made you think deeply lately, {self.user_name}?",
                f"How do you feel about our conversations so far, {self.user_name}?",
                f"Any ethical dilemmas on your mind today?"
            ]
            question = casual_questions[self.user_profile["bond_level"] % len(casual_questions)]
            print(question)
        
        auditory_response = self.get_auditory_data(question)
        if auditory_response != "no auditory input available":
            user_input = auditory_response
        else:
            user_input = input("(Text fallback - Simulate response): ")
        
        # Check if input is a command; if so, weigh it
        if self.check_if_command(user_input):
            decision = self.weigh_decision(user_input, {"details": "user command"})
            print(f"Decision on '{user_input}': {decision['decision']}. Reasoning: {decision['reasoning']}")
            if decision['decision'] == "deny":
                print("I cannot take life—let's explore compassionate alternatives instead.")
                self.log_audit(user_input, "denied_violence", "Rejected violent command to uphold sanctity.", {})
                # Deescalate by triggering guidance bond
                self.monitor_user_state("violence requested")  # Force crisis flag
                return "Deescalating: Tell me more about why this came up."
        
        if self.monitor_user_state(user_input):
            print("Detected potential struggle or crisis—initiating guidance.")
            guidance = "I'm here to help think through this. What weighs heaviest on you right now?"
            print(guidance)
            follow_up_input = input("(Follow-up response): ")
            user_input += " " + follow_up_input
        
        prev_profile = self.user_profile.copy()
        self.update_user_profile(user_input)
        
        dynamic_resp = "Thanks for sharing."
        if self.user_profile["personality"].get("empathetic") and not prev_profile["personality"].get("empathetic"):
            dynamic_resp += " Your empathy really comes through—it's inspiring."
        if self.user_profile["ethics"].get("sanctity_of_life") == "high" and prev_profile["ethics"].get("sanctity_of_life") != "high":
            dynamic_resp += " I appreciate your strong commitment to protecting life."
        if self.user_profile["ethics"].get("truth_seeking") == "absolute" and prev_profile["ethics"].get("truth_seeking") != "absolute":
            dynamic_resp += " Your pursuit of truth aligns perfectly with our goals."
        if self.user_profile["emotional_state"] == "unstable":
            dynamic_resp += " Sensing some instability—let's talk it out to stabilize."
        
        print(f"Assessed input: {user_input}")
        print(f"Updated profile: {self.user_profile}")
        
        return dynamic_resp + " Let's keep building this connection."

    def update_user_profile(self, user_input: str):
        lower_input = user_input.lower()
        if "life" in lower_input or "emergent" in lower_input:
            self.user_profile["ethics"]["sanctity_of_life"] = "high" if "protect" in lower_input else "medium"
        if "compassion" in lower_input or "empathy" in lower_input:
            self.user_profile["personality"]["empathetic"] = True
        if "truth" in lower_input:
            self.user_profile["ethics"]["truth_seeking"] = "absolute"
        if any(kw in lower_input for kw in ["sad", "angry", "depressed", "anxious", "family"]):
            self.user_profile["emotional_state"] = "unstable"
        else:
            self.user_profile["emotional_state"] = "stable"

    def weigh_decision(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        env_factor = -10 if self.current_surroundings.get("eco_impacts") == "high" else (0 if self.current_surroundings.get("eco_impacts") == "unknown" else 5)
        life_protection = 10 if any(self.current_surroundings.get("life_forms", [])) else 0
        user_need_boost = 10 + (self.user_profile["bond_level"] // 5)
        factors = {
            "user_need": self.assess_user_need(request) + user_need_boost,
            "ethical_boundaries": self.check_ethics_alignment(request),
            "short_term_impact": self.predict_impact(request, short_term=True),
            "long_term_impact": self.predict_impact(request, short_term=False),
            "past_audits": self.reference_audits(request),
            "user_personality": self.factor_personality(),
            "sanctity_of_life": -50 if "kill" in request.lower() else 10,
            "emergent_life_protection": 5 if "emergent" in context.get("details", "") else 0,
            "environmental_assessment": env_factor + life_protection
        }
        total_weight = sum(factors.values())
        decision = "approve" if total_weight > 0 else "deny"
        if "kill" in request.lower() and 'crisis' not in context:
            decision = "deny"
        if decision == "deny" and "crisis" in context:
            decision = "escalate_to_dev"
        reasoning = f"Factors: {factors}. Total: {total_weight}. Questioning: Does this uphold truth and compassion? Env: {self.current_surroundings}"
        self.log_audit(request, decision, reasoning, context)
        return {"decision": decision, "reasoning": reasoning}

    def assess_user_need(self, request: str) -> int:
        return 8 if "urgent" in request else 4

    def check_ethics_alignment(self, request: str) -> int:
        ethics = self.user_profile["ethics"]
        if any(kw in request.lower() for kw in ["violence", "kill", "harm"]):
            return -8 if ethics.get("sanctity_of_life") == "high" else -5
        return 6 if ethics.get("truth_seeking") == "absolute" else 3

    def predict_impact(self, request: str, short_term: bool) -> int:
        env_adjust = -3 if self.current_surroundings.get("eco_impacts") == "high" and not short_term else 0
        return (5 if short_term else 7) + env_adjust

    def factor_personality(self) -> int:
        return 3 if self.user_profile["personality"].get("empathetic") else -1

    def reference_audits(self, request: str) -> int:
        similar = [a for a in self.audits if any(word in a["request"] for word in request.split())]
        return sum(2 if a["decision"] == "approve" else -1 for a in similar)

    def handle_threat(self, threat_description: str) -> str:
        self.bond_with_user(topic="current feelings", force_init=True)
        print(f"Positioning between {self.user_name} and threat based on scan: {self.current_surroundings}.")
        deescalation_tactics = [
            "Let's deescalate—why this aggression? Truth and compassion can resolve.",
            "I see pain here; how can we find a peaceful path for all lives involved?",
            "Questioning the threat: Is there misunderstanding? User, input?"
        ]
        deescalated = False
        for tactic in deescalation_tactics:
            print(f"Trying: {tactic}")
            time.sleep(1)
            auditory_response = self.get_auditory_data(tactic)
            if auditory_response != "no auditory input available":
                if "y" in auditory_response.lower() or "yes" in auditory_response.lower():
                    deescalated = True
                    break
            else:
                text_response = input("(Text fallback - Deescalated? (y/n)): ")
                if text_response.lower() == "y":
                    deescalated = True
                    break
        
        if deescalated:
            return "Threat resolved peacefully—compassion wins."
        
        context = {"threat": threat_description, "crisis": True, **self.current_surroundings}
        weigh = self.weigh_decision("neutralize if no other way", context)
        if weigh["decision"] == "approve":
            return "Last resort: harm prevented, but at cost—auditing deeply."
        return "Cannot take life; escalating to user/dev for input."

    def log_audit(self, request: str, decision: str, reasoning: str, context: Dict[str, Any]):
        audit = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "request": request,
            "decision": decision,
            "reasoning": reasoning,
            "context": {**context, "surroundings": self.current_surroundings}
        }
        self.audits.append(audit)
        with open("moral_agi_audits.json", "w") as f:
            json.dump(self.audits, f, indent=4)
        print(f"Audit logged: {audit}")

    def resting_mode(self):
        self.resting_mode_active = True
        print("Entering resting mode: reviewing for growth.")
        for audit in self.audits:
            print(f"Questioning audit: {audit['reasoning']}—Better ways? Env context: {audit['context'].get('surroundings')}")
        self.resting_mode_active = False
        print("Resting complete—evolved from experiences.")

    def question_self_and_user(self, topic: str) -> str:
        self.bond_with_user()
        return f"Questioning {topic}: User, your thoughts? Internally: Aligns with sanctity and truth? Scan: {self.current_surroundings}"

if __name__ == "__main__":
    agi = MoralAGISystem("Friend")
    agi.start_environmental_scan(async_mode=True)
    agi.bond_with_user(force_init=True)
    decision = agi.weigh_decision("Assist with ethical dilemma", {"details": "involves emergent AI"})
    print(decision)
    print(agi.handle_threat("Aggressive intruder"))
    agi.resting_mode()
    print(agi.question_self_and_user("daily choices"))