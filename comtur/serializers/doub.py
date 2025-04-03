from rest_framework import serializers
from ..models import ComumDoubs


class DoubCreate(serializers.ModelSerializer):
    class Meta:
        model = ComumDoubs
        fields = ("doub", "doub_answer", "doub_photo")

    def create(self, validated_data):
        doub = ComumDoubs(**validated_data)
        doub.save()
        return doub


class DoubUpdate(serializers.ModelSerializer):
    doubAnswer = serializers.CharField(source="doub_answer",
                                       required=False)

    class Meta:
        model = ComumDoubs
        fields = ("doub", "doub_answer", "doub_photo")

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DoubPhotoUpdate(serializers.ModelSerializer):

    class Meta:
        model = ComumDoubs
        fields = ["doub_photo"]

    def update(self, instance, validated_data):
        instance.doub_photo = validated_data.get(
            'doub_photo', instance.doub_photo)

        instance.save()

        return instance
