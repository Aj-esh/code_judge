from rest_framework import serializers

class ProblemActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['run', 'submit', 'testcase'])
    code = serializers.CharField()
    language = serializers.ChoiceField(choices=['py', 'cpp', 'c'], default='py')
    cinput = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """
            Validation to ensure `cinput` is provided for the `testcase` action.
        """
        if data['action'] == 'testcase' and not data.get('cinput'):
            raise serializers.ValidationError({"cinput": "This field is required for the 'testcase' action."})
        return data