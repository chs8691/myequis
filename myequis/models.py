from django.db import models


# A species defines a set of components
class Species(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)


# A bicycle is structured into components. For instance front wheel, gear etc.
class Component(models.Model):
    name = models.CharField(max_length=100)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


# A bicycle has a species with has components which are maintained
class Bicycle(models.Model):
    name = models.CharField(max_length=100)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


# Parts of a component. For instance front wheel: tube, tire, left spokes.
# This is a simplified model of the real world. There is no position within a part, e.g. spokes(1)
class Part(models.Model):
    name = models.CharField(max_length=100)

    component = models.ForeignKey(Component, on_delete=models.CASCADE)

    def __str__(self):
        return "{}/{}/{}".format(self.component.species.name, self.component.name, self.name)


# Point in time of a bycicle to record its data
class Record(models.Model):
    date = models.DateField()
    km = models.DecimalField(max_digits=10, decimal_places=0, )

    bicycle = models.ForeignKey(Bicycle, on_delete=models.CASCADE)

    def __str__(self):
        return "{} {}".format(str(self.date), str(self.bicycle.name))


# A material is a physically part of a bicycle. It can be installed at removed, but it must not be used, e.g. when a
# new tube is bought, it has yet no relation to an bicyle.
class Material(models.Model):
    name = models.CharField(max_length=100)

    manufacture = models.CharField(max_length=100)
    size = models.CharField(max_length=100, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

    comment = models.CharField(max_length=50, blank=True, default="")

    disposed = models.BooleanField(default=False)
    disposedAt = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(f"{self.id}/{self.manufacture}/{self.name}/{self.disposedAt}")


class Mounting(models.Model):

    material = models.ForeignKey(Material, related_name="material", on_delete=models.CASCADE)

    mount_record = models.ForeignKey(Record, related_name="mount_record", on_delete=models.CASCADE)

    part = models.ForeignKey(Part, on_delete=models.CASCADE)

    comment = models.CharField(max_length=50, blank=True, default="")

    # Optional
    dismount_record = models.ForeignKey(Record, related_name="dismount_record", on_delete=models.CASCADE, blank=True,
                                        null=True)

    @property
    def active(self):
        return self.dismount_record is None


    def __str__(self):
        return "{}/{}/{} {} active={}".format(str(self.mount_record.bicycle.name),
                                              str(self.part.name),
                                              str(self.material.name),
                                              str(self.mount_record.date),
                                              str(self.active),
                                              str(self.comment),
                                              )
