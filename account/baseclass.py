from rest_framework.response import Response
from rest_framework.views import APIView


class AbstractBaseClassApiView(APIView):
    @property
    def serializer_class(self):
        # Our serializer depending on type
        raise NotImplementedError

    @property
    def model(self):
        # Our model depending on type
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        try:
            x = self.model.objects.all()
            ser = self.serializer_class(x, many=True)
            return Response(ser.data)
        except self.model.DoesNotExist:
            return Response(ser.errors)

    def post(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors)
