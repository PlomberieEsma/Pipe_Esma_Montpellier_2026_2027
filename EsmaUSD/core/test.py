from EsmaUSD.core.core import get_core

core = get_core()

def test():

    core.popup("Aucune task assignée à cette scène : impossible d'exporter l'asset/shot en USD.", title="Export USD", icon="warning")