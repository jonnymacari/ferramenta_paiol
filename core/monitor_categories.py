# Categorias de Monitores e Valores conforme documento

CATEGORIAS_MONITOR = (
    ('conselheiro_senior', 'Conselheiro Senior'),
    ('conselheiro', 'Conselheiro'),
    ('monitor', 'Monitor'),
    ('monitor_junior', 'Monitor Junior'),
    ('estagiario', 'Estagiário'),
    ('day_camp', 'Day Camp'),
    ('enfermeira', 'Enfermeira'),
    ('enfermeira_estagiaria', 'Enfermeira Estagiária'),
    ('fotografo_1', 'Fotógrafo 1'),
    ('fotografo_2', 'Fotógrafo 2'),
)

VALORES_DIARIAS = {
    'conselheiro_senior': 245.00,
    'conselheiro': 245.00,
    'monitor': 210.00,
    'monitor_junior': 170.00,
    'estagiario': 0.00,
    'day_camp': 180.00,
    'enfermeira': 170.00,
    'enfermeira_estagiaria': 170.00,
    'fotografo_1': 260.00,
    'fotografo_2': 170.00,
}

CATEGORIAS_AJUDA_CUSTO = (
    ('ajuda_1', 'Ajuda de Custo 1'),
    ('ajuda_2', 'Ajuda de Custo 2'),
    ('ajuda_3', 'Ajuda de Custo 3'),
)

VALORES_AJUDA_CUSTO = {
    'ajuda_1': 90.00,
    'ajuda_2': 145.00,
    'ajuda_3': 265.00,
}

def get_valor_diaria(categoria):
    """Retorna o valor da diária para uma categoria"""
    return VALORES_DIARIAS.get(categoria, 0.00)

def get_valor_ajuda_custo(categoria):
    """Retorna o valor da ajuda de custo para uma categoria"""
    return VALORES_AJUDA_CUSTO.get(categoria, 0.00)
