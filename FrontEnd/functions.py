def segmentar(segmento, lista_segmentar):
    list = []
    list_aux = []
    for indice, product in enumerate(lista_segmentar):
        list_aux.append(product)
        if (indice+1)%segmento == 0:
            list.append(list_aux)
            list_aux = []
    list.append(list_aux)
    return list