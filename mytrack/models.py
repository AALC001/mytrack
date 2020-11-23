import datetime
#from dateutil import relativedelta
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MaxValueValidator
#from multiselectfield import MultiSelectField
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from string import ascii_uppercase, digits
import re
# Create your models here.

class TimedModel(models.Model):

	creation_time = models.DateTimeField(auto_now_add=True, verbose_name="Date de creation")
	update_time = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

	class Meta:
		abstract = True


class Patient(TimedModel):
	code_patient = models.CharField("Code Patient",
				max_length=20, blank=False, unique=True)
	sexe = models.CharField(max_length=15, 
				blank=True, null=True)
	date_naissance = models.DateField("Date de Naissance", 
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	date_enrolement = models.DateField("Date d'enrolement", 
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	Date_de_mise_sous_ARV = models.DateField("Date de mise sous traitement ARV", 
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	nom_conseiller = models.CharField("Nom et Prénoms du conseiller",
				max_length=50, blank=True, null=True)

	def __str__(self):
		return self.code_patient

	@property
	def age(self):
		if self.date_naissance is None:
			return None
		else:
			return int(datetime.datetime.now().year) - int(self.date_naissance.year)

	@property
	def statut_ARV(self):
		if str(datetime.datetime.now() - datetime.timedelta(days=14))< str(self.date_fin_traitement) < str(datetime.datetime.now()):
			return "Pctif avec rupture"
		elif str(datetime.datetime.now() - datetime.timedelta(days=27)) < str(self.date_fin_traitement) < str(datetime.datetime.now() - datetime.timedelta(days=14)):
			return "Perdu de vu"
		elif str(self.date_fin_traitement) < str(datetime.datetime.now() - datetime.timedelta(days=27)):
			return "Perdu de vu (à remettre à la communauté)"
		else:
			return "Actif sans rupture"
		
	#@property
	#def cohorte_actuelle(self):
	#	if self.Date_de_mise_sous_ARV is None:
	#		return '0'
	#	else:
	#		today = datetime.datetime.now()
	#		diff_mois = (today.year - self.Date_de_mise_sous_ARV.year) *12 + today.month - self.Date_de_mise_sous_ARV.month + 1
	#		return "M{}".format(str(diff_mois))

class ChargeVirale(TimedModel):
	code_patient = models.ForeignKey("Patient", 
				on_delete=models.CASCADE, blank=True, null=True, related_name="charge_virale")
	date_prelevement = models.DateField("Date de prélèvement", 
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	resultat_CV = models.CharField("Résultat Charge Virale",
				max_length=20, blank=True, null=True)

	class Meta:
		verbose_name = "Charge Virale"
		verbose_name_plural = "Charges Virales"

	@property
	def sexe(self):
		return self.code_patient.sexe
	
	@property
	def nom_conseiller(self):
		return self.code_patient.nom_conseiller

# 
class Ordonnance(TimedModel):
	code_patient = models.ForeignKey("Patient", 
				on_delete=models.CASCADE, blank=True, null=True, related_name="ordonnance")
	date_derniere_dispensation = models.DateField("Date de dernière dispensation", 
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	nb_jour_traitement = models.PositiveIntegerField("Nombre de jour de traitement", 
				blank=True, null=True)
	dernier_regime_dispense = models.CharField("Dernier redime dispensé",
				max_length=20, blank=True, null=True)
	date_fin_traitement = models.DateField("Date de fin de Traitement", 
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	
	class Meta:
		verbose_name = "Ordonnance"
		verbose_name_plural = "Ordonnances"

	@property
	def statut_ARV(self):
		if str(datetime.datetime.now() - datetime.timedelta(days=14))< str(self.date_fin_traitement) < str(datetime.datetime.now()):
			return "Actif avec rupture de 0-14 jours"
		elif str(datetime.datetime.now() - datetime.timedelta(days=27)) < str(self.date_fin_traitement) < str(datetime.datetime.now() - datetime.timedelta(days=14)):
			return "Actif avec rupture de 15-27 jours"
		elif str(self.date_fin_traitement) < str(datetime.datetime.now() - datetime.timedelta(days=27)):
			return "Perdu de vue"
		else:
			return "Actif sans rupture"


	# @property
	# def presence_en_soins(self):
	# 	return self.code_patient.presence_soins
	
	# @property
	# def nom_et_prenoms(self):
	# 	return self.code_patient.nom_prenoms
	
	@property
	def sexe(self):
		return self.code_patient.sexe
	
	@property
	def nom_conseiller(self):
		return self.code_patient.nom_conseiller
	
	

	#@property
	#def statut_RDV(self):
	#	if str(self.derniere_relance) < str(self.derniere_visite):
	#		return "patients_venus"
	#	else :
	#		return "patients_non_venus"
	#@property
	#def passassion(self):
	#	date1 = datetime.timedelta(days=92)
	#	date2 = self.date + date1
	#	if str(datetime.datetime.now()) > str(date2) :
	#		return "A remettre aux conseillères communautaires"
	#	else:
	#		return "En vigueur"


class ContactSujetIndex(TimedModel):
	code_patient = models.ForeignKey("Patient", 
				on_delete=models.CASCADE, blank=True, null=True, related_name="contact_sujet_index")
	code_contact = models.CharField("Code du sujet contact",
				max_length=30, blank=True, null=True, unique=True)
	TYPE = (
		('1', 'Conjoint'),
		('2', 'Autre partenaire sexuel'),
		('3', 'Enfant biologique < 15 ans'),
		('4', 'Frères /Sœurs   < 15 ans (de index < 15 ans)'),
		('5', "Père/Mère(de l'index < 15 ans)"),
	)
	type_contact = models.CharField("Type de contact",
				max_length=1, blank=True, null=True, choices=TYPE)
	SEXE = (
		('1', 'Masculin'),
		('2', 'Feminin '),
		('3', 'Transgenre'),
	)
	sexe_contaxt = models.CharField("Sexe du contact",
				max_length=5, blank=True, null=True,choices=SEXE)
	date_naissance = models.DateField("Date de naissance",
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	STATUT = (
		('1', 'VIH +'),
		('2', 'VIH -'),
		('3', 'Inconnu'),
	)
	statut_identification = models.CharField("Statut VIH à l'enregistrement",
				max_length=1, blank=True, null=True, choices=STATUT)
	date_depistage = models.DateField("Date de dépistage",
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	RESULT_VIH = (
		('1', 'Positif'),
		('2', 'Négatif'),
	)
	resultat_depistage = models.CharField("Résultat de dépistage",
				max_length=1, blank=True, null=True, choices=RESULT_VIH)
	date_mise_ARV = models.DateField("Date de Mise sous ARV",
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])

	class Meta:
		verbose_name = "Contact du sujet Index"
		verbose_name_plural = "Contacts du sujet Index"
	
	@property
	def age(self):
		if self.date_naissance is None:
			return None
		else:
			return int(datetime.datetime.now().year) - int(self.date_naissance.year)

	# @property
	# def presence_en_soins(self):
	# 	return self.code_patient.presence_soins
	
	# @property
	# def nom_et_prenoms(self):
	# 	return self.code_patient.nom_prenoms
	
	@property
	def sexe_patient(self):
		return self.code_patient.sexe
	
	@property
	def nom_du_conseiller(self):
		return self.code_patient.nom_conseiller



class Rdv(TimedModel):
	code_patient = models.ManyToManyField("Patient", 
				verbose_name='code du patient')
	date_rdv = models.DateField("Date de Rendez-Vous", 
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	MOTIF_RDV = (
		('ARV', 'ARV'),
		('CV', 'CV'),
		('ETP', 'ETP'),
	)
	motif = MultiSelectField("Motif de Rendez-Vous", 
				choices=MOTIF_RDV)

	class Meta:
		verbose_name = "Rendez-Vous"
		verbose_name_plural = "Rendez-Vous"
	

class Respect(TimedModel):
	date_respect = models.DateField("Date de Respect", 
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	motif_respect = models.CharField("Respect de Rendez-Vous", 
				max_length=30, blank=True, null=True,)

	class Meta:
		verbose_name = "Respect de RDV"
		verbose_name_plural = "Respect des RDV"


#class Synthese(TimedModel):
#	motif = 

class SuiviRdv(TimedModel):
	code_patient = models.ForeignKey("Patient",
				on_delete=models.CASCADE, blank=True, null=True, related_name="suivi_rdv")
	rdv = models.ForeignKey("Rdv",
				on_delete=models.CASCADE, blank=True, null=True, related_name="suivi_rdv", editable=False)
	date_rappel = models.DateField("Date de Rappel",
				blank=True, null=True, validators = [MaxValueValidator(datetime.datetime.now().date())])
	moyen_rappel = models.CharField("Moyen de Rappel",
				max_length=20, blank=True, null=True)
	resultat = models.CharField("Resultat", 
				max_length=20, blank=True, null=True)
	RESPECT = (
		('OUI', 'OUI'),
		('NON', 'NON'),
	)
	respect_rdv = models.CharField("Respect de Rendez-Vous",
				max_length=3, blank=True, null=True, choices=RESPECT)
	date_respect = models.ForeignKey("Respect", 
				on_delete=models.CASCADE, blank=True, null=True, related_name="suivi_rdv")
	#synthese_rdv = models.ForeignKey("Synthese", 
	#			on_delete=models.CASCADE, blank=True, null=True, related_name="suivi_rdv")

	class Meta:
		verbose_name = "Suivi de RDV"
		verbose_name_plural = "Suivis des RDV"