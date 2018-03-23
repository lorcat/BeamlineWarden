__author__ = 'Konstantin Glazyrin'

from app.plugins.plugins_common import *

from app.workers import *
import threading

# tackt=2- in units of 2 base ticks (i.e. 0.2s for daemon basetick = 0.1s)
TICKTACK = 50.
# an offset shift by a some ticks
TICKTACK_OFFSET = 0.
# root ref
ROOT_REF = "P022.vacuum.interlock"
# PyTango Device
DEV_NAME = "haspp02oh1:10000/hasylab/vac.intlk/p02"


def setup(obj):
    """
    Test for the correct initialization and parameter presence
    :param obj:
    :return:
    """
    global TICKTACK, TICKTACK_OFFSET, DEV_NAME, ROOT_REF
    if not obj.test(TICKTACK):
        raise NameError
    if not obj.test(TICKTACK_OFFSET):
        raise NameError
    if not obj.test(DEV_NAME):
        raise NameError
    if not obj.test(ROOT_REF):
        raise NameError


def work(unlock=False):
    """
    Main work done by the plugin
    :param unlock:
    :return:
    """
    global ROOT_REF, DEV_NAME
    id = os.path.basename(__file__)

    # process vacuum components #1
    root_ref = ROOT_REF

    worker = PyTangoWorker(DEV_NAME, def_file=id, debug_level=logging.DEBUG)

    # manual unlock
    if unlock:
        worker.debug("Manual unlock")
        worker.unlock()

    # check lock
    if worker.is_locked():
        worker.debug("Operation is locked")
        return

    # lock
    worker.lock()

    try:
        attrs = ["T_EXP_P_02_2_MODE",
                "T_PS_1_A",
                "FRONTEND_MODE",
                "SVK_10_ON",
                "C_V_22_A",
                "DL_GESAMT_OK",
                "T_SVK_10_RESET",
                "SI111_LAUE_OK",
                "EtherCAT_OK",
                "BS_A1",
                "T_V_23_A",
                "TE_GESAMT_OK",
                "P_22_PEAKS",
                "C_PS_2_A",
                "KW_FROND_1_H_QS",
                "C111_LAUE_OK",
                "C_V_1_A",
                "C_LM_0_S",
                "OAB",
                "T_SVK_20_RESET",
                "BS_A1_A_F",
                "SCHLUESSEL_FREIGABE",
                "PS_0",
                "SSK_OK",
                "PS_1",
                "P_11_PEAKS",
                "PS_2",
                "BS_B1",
                "T_LM_12_S",
                "C_V_24_A",
                "T_N2_UEBERWACHUNG_AUS",
                "T_LM_20_S",
                "C_LM_11_S",
                "C_V_10_A",
                "P_10",
                "LM_0",
                "P_11",
                "LM_1",
                "P_21_PEAKS",
                "SV_L_OK",
                "SVK_0_ON",
                "KW_GESAMT_OK",
                "BS_0_S_V",
                "T_SVK_0_RESET",
                "DL_EXP_P_02_2_OK",
                "SVK_11_ON",
                "P_10_PEAKS",
                "FRONTEND_OFFEN",
                "P_20",
                "P_21",
                "P_22",
                "P_23",
                "P_24",
                "DL_FRONTEND_1_OK",
                "T_V_20_A",
                "C_LM_1_S",
                "SV_E_OK",
                "KW_FROND_1_E_QS",
                "P_20_PEAKS",
                "LM_10",
                "LM_11",
                "DL_FRONTEND_5_OK",
                "LM_12",
                "BS_0",
                "PETRA_STROM_GERING",
                "UND",
                "SSK_AlarmAusgeloest",
                "SSK_AlarmOffen",
                "KR_311_HHL_OK",
                "C_V_11_A",
                "SSK_AUSGEL",
                "T_SVK_1_RESET",
                "LM_20",
                "LM_21",
                "C111_LAUE",
                "EXP_P_02_1_MODE",
                "CRYO_HHL_OK",
                "T_LAS_S",
                "T_EXP_P_02_1_MODE",
                "N2_DIAMANTFENSTER_OK",
                "F_PS_2_A",
                "SSK_UEBERSTR",
                "C_FIL_0_S",
                "C_LAS_S",
                "P_0",
                "P_1",
                "T_OPTIK_MODE",
                "T_LM_21_S",
                "STRAHL_BIS_EXP_2",
                "C_LM_10_S",
                "T_FIL_0_S",
                "T_V_11_A",
                "DL_OPTIK_1_OK",
                "LAS",
                "FIL_0",
                "FIL_1",
                "NO_DUMP",
                "KR_111_HHL_OK",
                "K_HHL_OK",
                "T_LM_10_S",
                "C_LM_21_S",
                "SSK_FREIGABE",
                "SI111_LAUE",
                "C_V_20_A",
                "T_LM_1_S",
                "C_V_12_A",
                "EXP_P_02_2_Freigabe",
                "SVK_20_ON",
                "SVK_1_ON",
                "SSK_OFFEN",
                "KW_OPTIK_1_H_QS",
                "P_R",
                "DL_EXP_P_02_1_OK",
                "V_10",
                "V_11",
                "BS_B1_A_F",
                "T_V_0_A",
                "V_12",
                "P_1_PEAKS",
                "P_R_PEAKS",
                "DL_FRONTEND_2_OK",
                "T_FRONTEND_MODE",
                "OPTIK_MODE",
                "OPTIK_BEREIT",
                "T_V_22_A",
                "V_20",
                "V_21",
                "V_22",
                "V_23",
                "DL_FRONTEND_6_OK",
                "HW_GESAMT_OK",
                "V_24",
                "SSK_SCHARF",
                "T_SVK_12_RESET",
                "V_0",
                "V_1",
                "T_PS_2_A",
                "C_V_21_A",
                "P_0_PEAKS",
                "P_24_PEAKS",
                "SSK_AlarmSummme",
                "SVK_12_ON",
                "SVK_21_ON",
                "T_V_24_A",
                "HHL_OK",
                "C_PS_1_A",
                "T_FIL_1_P",
                "C_V_0_A",
                "T_V_1_A",
                "T_V_10_A",
                "T_SVK_11_RESET",
                "SSK_AlarmUeberstrom",
                "T_LM_11_S",
                "C_LM_20_S",
                "C_V_23_A",
                "T_V_21_A",
                "DL_OPTIK_2_OK",
                "SSK_OBEN",
                "C_LM_12_S",
                "P_23_PEAKS",
                "T_LM_0_S",
                "UND_F",
                "Tickdog",
                "VSE",
                "T_SVK_21_RESET",
                "EXP_P_02_2_MODE"]

        # get all values - in sequence
        data = {}
        values = worker.read_attributes(attrs)

        worker.debug(values)

        bfailed = False
        if (not worker.test(values)) or len(values) == 0 or (None in values and 0 not in values and 1 not in values):
            worker.debug("There is an error with a device - we can only set default values")
            bfailed = True

        for (i, attr) in enumerate(attrs):
            if not bfailed:
                value = values[i]
                if attr.lower() == "state":
                    value = str(value)
                data[attr] = value
            else:
                data[attr] = None

        # worker.debug("dict. values {}".format(data))

        # convert dict to json string, save the key
        dict2json(root_ref, data, worker)
    except Exception as e:
        worker.error("Critical error, message is:\n{}".format(e.message))

    # unlock
    worker.unlock()

if __name__=="__main__":
    work(unlock=True)

#TODO: done 20170808