# g:\Meu Drive\Antigravity\Finançals Analysis (1)\utils\sector_map.py

SECTOR_MAP = {
    # Financeiro
    'ITUB': 'Financeiro', 'ITUB4': 'Financeiro',
    'BBDC': 'Financeiro', 'BBDC4': 'Financeiro', 'BBDC3': 'Financeiro',
    'BBAS': 'Financeiro', 'BBAS3': 'Financeiro',
    'SANB': 'Financeiro', 'SANB11': 'Financeiro',
    'B3SA': 'Financeiro', 'B3SA3': 'Financeiro',
    'BPAC': 'Financeiro', 'BPAC11': 'Financeiro',
    
    # Petróleo, Gás e Biocombustíveis
    'PETR': 'Petróleo/Energia', 'PETR4': 'Petróleo/Energia', 'PETR3': 'Petróleo/Energia',
    'PRIO': 'Petróleo/Energia', 'PRIO3': 'Petróleo/Energia',
    'RRRP': 'Petróleo/Energia', 'RRRP3': 'Petróleo/Energia',
    'VBBR': 'Petróleo/Energia', 'VBBR3': 'Petróleo/Energia',
    'UGPA': 'Petróleo/Energia', 'UGPA3': 'Petróleo/Energia',
    
    # Materiais Básicos (Mineração, Siderurgia, Papel)
    'VALE': 'Materiais Básicos', 'VALE3': 'Materiais Básicos',
    'GGBR': 'Materiais Básicos', 'GGBR4': 'Materiais Básicos',
    'CSNA': 'Materiais Básicos', 'CSNA3': 'Materiais Básicos',
    'USIM': 'Materiais Básicos', 'USIM5': 'Materiais Básicos',
    'KLBN': 'Materiais Básicos', 'KLBN11': 'Materiais Básicos',
    'SUZB': 'Materiais Básicos', 'SUZB3': 'Materiais Básicos',
    
    # Utilidade Pública (Energia Elétrica, Saneamento)
    'ELET': 'Utilidade Pública', 'ELET3': 'Utilidade Pública', 'ELET6': 'Utilidade Pública',
    'CPLE': 'Utilidade Pública', 'CPLE6': 'Utilidade Pública',
    'CMIG': 'Utilidade Pública', 'CMIG4': 'Utilidade Pública',
    'EQTL': 'Utilidade Pública', 'EQTL3': 'Utilidade Pública',
    'SBSP': 'Utilidade Pública', 'SBSP3': 'Utilidade Pública',
    'CPFE': 'Utilidade Pública', 'CPFE3': 'Utilidade Pública',
    
    # Consumo Não Cíclico
    'ABEV': 'Consumo', 'ABEV3': 'Consumo',
    'JBSS': 'Consumo', 'JBSS3': 'Consumo',
    'BRFS': 'Consumo', 'BRFS3': 'Consumo',
    'MRFG': 'Consumo', 'MRFG3': 'Consumo',
    'ASAI': 'Consumo', 'ASAI3': 'Consumo',
    'CRFB': 'Consumo', 'CRFB3': 'Consumo',
    
    # Consumo Cíclico (Varejo, Construção)
    'MGLU': 'Varejo/Consumo', 'MGLU3': 'Varejo/Consumo',
    'VIIA': 'Varejo/Consumo', 'VIIA3': 'Varejo/Consumo', 'BHIA3': 'Varejo/Consumo',
    'LREN': 'Varejo/Consumo', 'LREN3': 'Varejo/Consumo',
    'AMER': 'Varejo/Consumo', 'AMER3': 'Varejo/Consumo',
    'CURY': 'Construção', 'CURY3': 'Construção',
    'MRVE': 'Construção', 'MRVE3': 'Construção',
    'DIRR': 'Construção', 'DIRR3': 'Construção',
    'CYRE': 'Construção', 'CYRE3': 'Construção',
    
    # Saúde
    'RDOR': 'Saúde', 'RDOR3': 'Saúde',
    'HAPV': 'Saúde', 'HAPV3': 'Saúde',
    'RADL': 'Saúde', 'RADL3': 'Saúde',
    'FLRY': 'Saúde', 'FLRY3': 'Saúde',
    
    # Tecnologia e Comunicações
    'TOTS': 'Tecnologia', 'TOTS3': 'Tecnologia',
    'VIVT': 'Comunicações', 'VIVT3': 'Comunicações',
    'TIMS': 'Comunicações', 'TIMS3': 'Comunicações',
    
    # Transportes
    'WEGE': 'Bens Industriais', 'WEGE3': 'Bens Industriais',
    'RAIL': 'Bens Industriais', 'RAIL3': 'Bens Industriais',
    'AZUL': 'Transporte', 'AZUL4': 'Transporte',
    'GOLL': 'Transporte', 'GOLL4': 'Transporte',
    'RENT': 'Transporte', 'RENT3': 'Transporte',
}

def get_sector(symbol):
    """Returns the sector based on ticker, stripping numbering."""
    if not isinstance(symbol, str): return "Outros"
    symbol = symbol.strip().upper()
    
    # Try exact match first
    if symbol in SECTOR_MAP:
        return SECTOR_MAP[symbol]
    
    # Try match without trailing numbers (VALE3 -> VALE)
    base = ''.join([i for i in symbol if not i.isdigit()])
    return SECTOR_MAP.get(base, "Outros")
