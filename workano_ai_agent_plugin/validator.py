from wazo_confd.helpers.validator import Validator, ValidationGroup


class AIAgentValidator(Validator):
    def validate(self, model):
        return


def build_ai_agent_validator():
    ai_agent_validator = AIAgentValidator()
    return ValidationGroup(create=[ai_agent_validator], edit=[ai_agent_validator])

