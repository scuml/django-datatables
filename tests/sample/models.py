from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from decimal import Decimal

class Employee(models.Model):

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birthday = models.DateField()
    start_date = models.DateField()
    manager = models.ForeignKey('self', null=True)



class Sponsor(models.Model):

    sponsor_name = models.CharField(
        _('Sponsor name'),
        max_length=250, unique=True
    )

    def __unicode__(self):
        app_label = 'ecgps_core'
        return unicode(self.sponsor_name)

class Study(models.Model):

    STUDY_STATUS_CHOICES = (
        ('active', _(u'Active')),
        ('cancelled', _(u'Cancelled')),
        ('closed_completed', _(u'Closed/Completed')),
        ('implementing', _(u'Implementing')),
    )

    BANK_FUNDED_CHOICES = (
        ('wf_usd', _('Wells Fargo USD')),
        ('wf_eur', _('Wells Fargo EUR')),
        ('wf_gbp', _('Wells Fargo GBP')),
    )

    PHASE_CHOICES = (
        ("Pre-clinical studies", "Pre-clinical studies"),
        ("Phase 0", "Phase 0"),
        ("Phase I", "Phase I"),
        ("Phase II", "Phase II"),
        ("Phase III", "Phase III"),
        ("Phase IV", "Phase IV"),
        ("Phase V", "Phase V"),
    )

    STUDY_CLIENT_CHOICES = (
        ('Sponsor', 'Sponsor'),
        ('CRO', 'CRO'),
    )

    THERAPEUTIC_AREA_CHOICES = (
        ("Cardiology/Vascular Diseases", "Cardiology/Vascular Diseases"),
        ("Dental and Oral Health", "Dental and Oral Health"),
        ("Dermatology", "Dermatology"),
        ("Endocrinology", "Endocrinology"),
        ("Family Medicine", "Family Medicine"),
        ("Gastroenterology", "Gastroenterology"),
        ("Genetic Disease", "Genetic Disease"),
        ("Healthy Volunteers", "Healthy Volunteers"),
        ("Hematology", "Hematology"),
        ("Hepatology (Liver, Pancreatic, Gall Bladder)",
            "Hepatology (Liver, Pancreatic, Gall Bladder)"),
        ("Immunology", "Immunology"),
        ("Infections and Infectious Diseases",
            "Infections and Infectious Diseases"),
        ("Musculoskeletal", "Musculoskeletal"),
        ("Nephrology", "Nephrology"),
        ("Neurology", "Neurology"),
        ("Nutrition and Weight Loss", "Nutrition and Weight Loss"),
        ("Obstetrics/Gynecology", "Obstetrics/Gynecology"),
        ("Oncology", "Oncology"),
        ("Ophthalmology", "Ophthalmology"),
        ("Orthopedics/Orthopedic Surgery", "Orthopedics/Orthopedic Surgery"),
        ("Otolaryngology (Ear, Nose, Throat)",
            "Otolaryngology (Ear, Nose, Throat)"),
        ("Pediatrics/Neonatology", "Pediatrics/Neonatology"),
        ("Plastic Surgery", "Plastic Surgery"),
        ("Pharmacology/Toxicology", "Pharmacology/Toxicology"),
        ("Podiatry", "Podiatry"),
        ("Psychiatry/Psychology", "Psychiatry/Psychology"),
        ("Pulmonary/Respiratory Diseases", "Pulmonary/Respiratory Diseases"),
        ("Rheumatology", "Rheumatology"),
        ("Sleep", "Sleep"),
        ("Trauma (Emergency, Injury, Surgery)",
            "Trauma (Emergency, Injury, Surgery)"),
        ("Urology", "Urology"),
        ("Vaccines", "Vaccines"),
    )

    study_name = models.CharField(_(u'Study name'), max_length=250)
    slug = models.SlugField('Study slug', max_length=250)
    sponsor = models.ForeignKey(Sponsor)
    approval_levels = models.IntegerField(
        default=1,
        verbose_name=_("Number of approval levels required")
    )
    protocol = models.CharField(max_length=250)

    funding_threshold = models.DecimalField(
        decimal_places=2,
        max_digits=20,
        default=0,
    )
    bank_funded = models.CharField(
        default='wf_usd',
        help_text='GPH Bank to withdraw money from for this study',
        choices=BANK_FUNDED_CHOICES,
        blank=False,
        max_length=50,
    )
    # TODO: check if can be removed. No longer using this field
    service_charge_percent = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default='1.0',
        help_text='Enter as a percent - ex. 1.0'
    )
    # TODO: check if can be removed. No longer using this field
    basis_point = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default='0.75',
        help_text='Enter as a percent - ex. 0.75',
        verbose_name=_('Basis Point Percentage')
    )
    domestic_ach_fee = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default=Decimal('0.15'),
        help_text=_('Fee charged for a domestic ACH transaction')
    )

    international_ach_fee = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default=Decimal('0.15'),
        help_text=_('Fee charged for a international ACH transaction')
    )

    swift_wire_fee = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default=Decimal('25.00'),
        help_text=_('Fee charged for a domestic Wire transaction')
    )

    fed_wire_fee = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default=Decimal('13.00'),
        help_text=_('Fee charged for a international Wire transaction')
    )

    international_check_fee = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default=Decimal('100.00'),
        help_text=_('Fee charged for a international check transaction')
    )

    domestic_check_fee = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        default=Decimal('1.00'),
        help_text=_('Fee charged for a domestic check transaction')
    )


    phase = models.CharField(
        _('Phase'),
        max_length=250,
        blank=True,
        default='',
        choices=PHASE_CHOICES,
    )

    therapeutic_area = models.CharField(
        _('Therapeutic area'),
        max_length=250,
        blank=True,
        default='',
        choices=THERAPEUTIC_AREA_CHOICES,
    )


    activation_date = models.DateField(
        verbose_name='Activation date',
        null=True,
        blank=True,
    )

    completion_date = models.DateField(
        verbose_name='Completion date',
        null=True,
        blank=True,
    )

    estimated_duration = models.IntegerField(
        verbose_name=_('Estimated duration'),
        null=True,
        blank=True,
        help_text=_('Duration in months'),
    )

    study_status = models.CharField(
        _('Status'),
        max_length=50,
        blank=False,
        default='',
        choices=STUDY_STATUS_CHOICES,
    )

    client = models.CharField(
        'Client',
        max_length=250,
        blank=False,
        default='',
        choices=STUDY_CLIENT_CHOICES,
    )

    clinical_trials_gov_id = models.CharField(
        'ClinicalTrials.gov id',
        max_length=250,
        blank=True,
        default='',
        help_text=_('clinicaltrials.gov ID'),
    )

    # Fields below added for Amgen.
    client_dept_code = models.CharField(
        "Client department code",
        max_length=32,
        blank=True,
        default=''
    )

    client_alias = models.CharField(
        "Client alias",
        max_length=32,
        blank=True,
        default=''
    )

    def __unicode__(self):

        return self.study_name

    class Meta:

        unique_together = (
            ('sponsor', 'study_name'),
            ('sponsor', 'protocol'),
        )
        verbose_name = _('Study')
        app_label = 'ecgps_core'
