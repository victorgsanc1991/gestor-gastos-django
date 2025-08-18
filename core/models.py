from django.db import models

class Categoria(models.Model):
    TIPO_CHOICES = [('ingreso', 'Ingreso'), ('gasto', 'Gasto')]
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nombre

class Transaccion(models.Model):
    ESTADO_CHOICES = [('activo', 'Activo'), ('excluido', 'Excluido')]
    fecha_operacion = models.DateField()
    concepto_original = models.CharField(max_length=255)
    importe = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=8, choices=ESTADO_CHOICES, default='activo')
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.fecha_operacion} - {self.concepto_original}"

class Regla(models.Model):
    palabra_clave = models.CharField(max_length=100, unique=True)
    categoria_destino = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return f"'{self.palabra_clave}' -> {self.categoria_destino.nombre}"
