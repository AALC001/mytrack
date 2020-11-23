from django.contrib import admin
from .models import *
import datetime
from datetime import timedelta
from django.utils import timezone
from reversion.admin import VersionAdmin
from import_export import resources,fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from import_export import resources,fields,widgets

admin.site.site_header = 'MY_TRACK'
admin.site.site_title = 'MY_TRACK'
admin.site.index_title = "Espace d'administration"

class ChargeViraleInline(admin.TabularInline):
	model = ChargeVirale

class ContactSujetIndexInline(admin.TabularInline):
	model = ContactSujetIndex

class OrdonnanceInline(admin.TabularInline):
	model = Ordonnance

class RespectInline(admin.TabularInline):
	model = Respect

class PatientResource(resources.ModelResource):
	age = fields.Field(attribute='age')
	class Meta:
		model = Patient
		import_id_fields = ('code_patient',)
		fields=('code_patient', 'sexe', 'date_naissance', 'date_enrolement', 'Date_de_mise_sous_ARV', 'nom_conseiller',)
		export_order=('code_patient', 'sexe', 'date_naissance', 'date_enrolement', 'Date_de_mise_sous_ARV','nom_conseiller',)

@admin.register(Patient)
class PatientAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	resource_class = PatientResource
	list_display = ('code_patient', 'sexe', 'date_naissance', 'age', 'date_enrolement', 'Date_de_mise_sous_ARV','nom_conseiller',)
	search_fields=['code_patient',]

	inlines = [
		ChargeViraleInline,
		OrdonnanceInline,
		ContactSujetIndexInline,
	]

class ContactSujetIndexResource(resources.ModelResource):
	class Meta:
		model = ContactSujetIndex
		import_id_fields = ('code_contact',)
		fields=('code_contact','type_contact','sexe_contaxt', 'date_naissance', 'age', 'statut_identification',
		'date_depistage','resultat_depistage','nom_du_conseiller',)

@admin.register(ContactSujetIndex)
class ContactSujetIndexAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	resource_class = ContactSujetIndexResource
	list_display = ('code_patient','sexe_patient', 'code_contact', 'type_contact','sexe_contaxt',
	'date_naissance','statut_identification','date_depistage','resultat_depistage','nom_du_conseiller',)



class OrdonnanceResource(resources.ModelResource):
	class Meta:
		model=Ordonnance
		import_id_fields=('code_patient',)
		fields=('code_patient', 'date_derniere_dispensation', 'nb_jour_traitement','dernier_regime_dispense','date_fin_traitement',)
		export_order = ('code_patient', 'date_derniere_dispensation', 'nb_jour_traitement','dernier_regime_dispense','date_fin_traitement',)

@admin.register(Ordonnance)
class OrdonnanceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	resource_class = OrdonnanceResource
	list_display = ('code_patient', 'date_derniere_dispensation', 'nb_jour_traitement','dernier_regime_dispense','date_fin_traitement', 'statut_ARV',)



class ChargeViraleResource(resources.ModelResource):
	class Meta:
		model=ChargeVirale
		import_id_fields=('code_patient',)
		fields=('code_patient', 'date_prelevement', 'resultat_CV',)
		export_order = ('code_patient', 'date_prelevement', 'resultat_CV',)

@admin.register(ChargeVirale)
class ChargeViraleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	resource_class = ChargeViraleResource
	list_display = ('code_patient', 'date_prelevement', 'resultat_CV',)


class RdvResource(resources.ModelResource):
	class Meta:
		model=Rdv
		import_id_fields=('code_patient',)
		fields=('code_patient', 'date_rdv', 'motif',)
		export_order = ('code_patient', 'date_rdv', 'motif',)

@admin.register(Rdv)
class RdvAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	resource_class = RdvResource
	list_display = (#'code_patient', 
	'date_rdv', 'motif',)


class SuiviRdvResource(resources.ModelResource):
	class Meta:
		model=SuiviRdv
		import_id_fields=('code_patient',)
		fields=('code_patient', 'date_rappel', 'moyen_rappel','resultat', 'respect_rdv', 'date_respect',)
		export_order = ('code_patient', 'date_rappel', 'moyen_rappel','resultat', 'respect_rdv', 'date_respect',)

@admin.register(SuiviRdv)
class SuiviRdvAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	resource_class = RdvResource
	list_display = (#'get_code_patient', 
    'date_rappel', 'moyen_rappel','resultat', 'respect_rdv', 'date_respect',)

	Inline = [
		RespectInline,
	]

@admin.register(Respect)
class RespectAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    pass
