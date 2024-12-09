# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import pprint

from future.utils import iteritems

# standard 10-20 and 10-20 electrode names defined in the EDF+ standard
# the keys are the names, the values are the 16 byte long fixed string used by EDF advised to define the channel
# T1 and T2 are not standard names but are much used in clinical EEG and are equivalent to FT9 and FT10
# use REF for a non-specific reference, e.g., "EEG T3-REF"

std_electrode_names_fixedlen = dict(
    # 10-20
    # left
    Fp1="EEG Fp1         ",
    F7="EEG F7          ",
    T3="EEG T3          ",
    T5="EEG T5          ",
    O1="EEG O1          ",
    # left central chain
    F3="EEG F3          ",
    C3="EEG C3          ",
    P3="EEG P3          ",
    A1="EEG A1          ",
    # right
    Fp2="EEG Fp2         ",
    F8="EEG F8          ",
    T4="EEG T4          ",
    T6="EEG T6          ",
    O2="EEG O2          ",
    # right central chain
    F4="EEG F4          ",
    C4="EEG C4          ",
    P4="EEG P4          ",
    A2="EEG A2          ",
    # midline
    Cz="EEG Cz          ",
    Fz="EEG Fz          ",
    Pz="EEG Pz          ",
    # extended 10-20
    T1="EEG FT9         ",  # maybe I should map this to FT9/T1
    T2="EEG FT10        ",  # maybe I should map this to FT10/T2
    Pg1="EEG Pg1         ",
    Pg2="EEG Pg2         ",
    # now the uncommon ones
    Nz="EEG Nz          ",
    Fpz="EEG Fpz         ",
    # anterior frontal chain
    AF7="EEG AF7         ",
    AF8="EEG AF8         ",
    AF3="EEG AF3         ",
    AFz="EEG AFz         ",
    AF4="EEG AF4         ",
    # 10-10 frontal
    F9="EEG F9          ",
    # F7
    F5="EEG F5          ",
    # F3
    F1="EEG F1          ",
    # Fz
    F2="EEG F2          ",
    # F4
    F6="EEG F6          ",
    # F8
    F10="EEG F10         ",
    # Fronto-Temporal
    FT9="EEG FT9         ",  # same as T1
    FT7="EEG FT7         ",
    FC5="EEG FC5         ",
    FC3="EEG FC3         ",
    FC1="EEG FC1         ",
    FCz="EEG FCz         ",
    FC2="EEG FC2         ",
    FC4="EEG FC4         ",
    FC6="EEG FC6         ",
    FT8="EEG FT8         ",
    FT10="EEG FT10        ",  # same as T2
    # temporal *is* central
    T9="EEG T9          ",
    T7="EEG T7          ",
    C5="EEG C5          ",
    # C3
    C1="EEG C1          ",
    # Cz
    C2="EEG C2          ",
    # C4
    C6="EEG C6          ",
    T8="EEG T8          ",
    T10="EEG T10         ",
    # A2
    # T3
    # T4
    # T5
    # T6
    # Temporal (or Central) Parietal
    TP9="EEG TP9         ",
    TP7="EEG TP7         ",
    CP5="EEG CP5         ",
    CP3="EEG CP3         ",
    CP1="EEG CP1         ",
    CPz="EEG CPz         ",
    CP2="EEG CP2         ",
    CP4="EEG CP4         ",
    CP6="EEG CP6         ",
    TP8="EEG TP8         ",
    TP10="EEG TP10        ",
    # Parietal
    P9="EEG P9          ",
    P7="EEG P7          ",
    P5="EEG P5          ",
    # P3
    P1="EEG P1          ",
    # Pz
    P2="EEG P2          ",
    # P4
    P6="EEG P6          ",
    P8="EEG P8          ",
    P10="EEG P10         ",
    PO7="EEG PO7         ",
    PO3="EEG PO3         ",
    POz="EEG POz         ",
    PO4="EEG PO4         ",
    PO8="EEG PO8         ",
    # O1
    Oz="EEG Oz          ",
    # O2
    Iz="EEG Iz          ",
)
# check that all the lengths of the labels are 16
print(
    "all equal to 16:", all(len(v) == 16 for v in std_electrode_names_fixedlen.values())
)
# print([ len(v) for v in std_electrode_names_fixedlen.values()])

standard_10_10_electrodes = sorted(std_electrode_names_fixedlen.keys())
standard_edf_10_10_electrode_labels_strip = {
    k: v.strip() for k, v in iteritems(std_electrode_names_fixedlen)
}
label_strip2electrodes = {
    v: k
    for k, v in iteritems(standard_edf_10_10_electrode_labels_strip)
    if k != "T1" and k != "T2"
}
label2electrodes = {
    v: k for k, v in iteritems(std_electrode_names_fixedlen) if k != "T1" and k != "T2"
}

# pprint.pprint(standard_10_10_electrodes)
# print('-----------')
# pprint.pprint(standard_edf_10_10_electrode_labels_strip)

# print('---- labe2electrodes ---')
# pprint.pprint(label2electrodes)

# annotations
standard_annotations = [
    "Lights off",
    "Lights on",
    "Sleep stage W",
    "Sleep stage 1",
    "Sleep stage 2",
    "Sleep stage 3",
    "Sleep stage 4",
    "Sleep stage R",
    "Sleep stage ?",
    "Movement time",
    "Sleep stage N",
    "Sleep stage N1",
    "Sleep stage N2",
    "Sleep stage N3",
    "Apnea",
    "Obstructive apnea",
    "Central apnea",
    "Mixed apnea",
    "Hypopnea",
    "Obstructive hypopnea",
    "Central hypopnea",
    "Hypoventilation",
    "Periodic breathing",
    "CS breathing",
    "RERA",
    "Limb movement",
    "PLMS",
    "EEG arousal",
    "Sinus Tachycardia",
    "WC tachycardia",
    "NC tachycardia",
    "Bradycardia",
    "Asystole",
    "Atrial fibrillation",
    "Bruxism",
    "RBD",
    "RMD",
]

# note AASM uses N/N1/N2/N3 stages

# standard ECG are
# ECG derivation I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6, or
# -aVR, or V2R, V3R, V4R, V7, V8, V9, or X, Y, Z is recorded, then the
# 'Specification' of the ECG signal must equal the name of that
# derivation, for instance resulting in label 'ECG V2R

ecg_leads = [
    "I",
    "II",
    "III",
    "aVR",
    "aVL",
    "aVF",
    "V1",
    "V2",
    "V3",
    "V4",
    "V5",
    "V6",
    "-aVR",
    "V2R",
    "V3R",
    "V4R",
    "V7",
    "V8",
    "V9",
    "X",
    "Y",
    "Z",
]

ecg_labels = {
    k: "ECG %s" % k for k in ecg_leads
}  # these are not expanded to 16 characters

# there are EMG labels too but I will not add those yet
# these though are used for leg movement scoring for sleep
# EMG RAT
# EMG LAT
# "Resp nasal" <- label for nasal airflow
