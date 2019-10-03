from django.db import models

# A bicycle has Component which are maintained
class Bicycle(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



# A bicycle is structured into components. For instance front wheel, gear etc.
class Component(models.Model):

    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
# Parts of a component. For instance front wheel: tube, tire, left spokes. 
# This is a simplified model of the real world. There is no position within a part, e.g. spokes(1)
class Part(models.Model):

    name = models.CharField(max_length=100)

    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    
    def display_long_name(self):
        return "{}/{}".format(self.component.name, self.name)    
    
    def __str__(self):
        return "{}/{}".format(self.component.name, self.name)    

# Point in time of a bycicle to record its data
class Record(models.Model):

    date = models.DateField()
    km = models.DecimalField(max_digits=10, decimal_places=0, )
    
    bicycle = models.ForeignKey(Bicycle, on_delete=models.CASCADE)

    def __str__(self):
        return "{} {}".format(self.date, self.bicycle.name)


# A material is a physically part of a bicycle. It can be installed at removed, but it must not be used, e.g. when a new tube is bought, it has yet no relation to an bicyle. 
class Material(models.Model):

    name = models.CharField(max_length=100)
    
    manufactor = models.CharField(max_length=100)
    size = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, name="Weight [g]", blank=True, null=True)
    
    # Optional 
    part = models.ForeignKey(Part, on_delete=models.CASCADE, blank=True, null=True)

    # Optional 
    mount_record = models.ForeignKey(Record, related_name="mount_record", on_delete=models.CASCADE, blank=True, null=True)
    
    # Optional 
    dismount_record = models.ForeignKey(Record, related_name="dismount_record", on_delete=models.CASCADE, blank=True, null=True)
    
    def mounted_in_bicycle(self):
        if self.mount_record is None:
            return None
        
        return self.mount_record.bicycle.name
    
    def __str__(self):
        return self.name



