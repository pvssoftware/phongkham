from channels.generic.websocket import AsyncJsonWebsocketConsumer



class ListPatientsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print("connect")
        await  self.accept()
        await self.channel_layer.group_add("patients",self.channel_name)
        print(f"Add {self.channel_name} channel to patients's group")

    async def receive_json(self,message):
        print("receive",message)
    
    async def disconnect(self,close_code):
        print("disconnect")
        await self.channel_layer.group_discard("patients",self.channel_name)
        print(f"Remove {self.channel_name} channel to patients's group")

    async def patient_update(self,event):
        await self.send_json(event)
        print("user updated",event)