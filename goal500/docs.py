"""
Documentação do pacote goal500.

Este pacote extrai dados de gols acumulados por ano de jogadores de futebol da Wikipedia
e fornece ferramentas para visualização desses dados.
"""

# Documentação para o módulo scrapers.wikipedia
"""
Módulo para extrair dados de gols de jogadores de futebol da Wikipedia.

Funções:
    wiki_url(path): Constrói a URL completa da Wikipedia a partir de um caminho.
    get_active_players(): Retorna uma lista de jogadores ativos com seus nomes e links.
    extract_goals_by_year(url): Extrai os gols por ano de um jogador a partir da sua página.
    get_player_stats(): Obtém estatísticas de gols por ano para todos os jogadores ativos.
"""

# Documentação para o módulo utils.data_processing
"""
Módulo para processamento e manipulação de dados extraídos.

Funções:
    clean_data(df): Limpa e prepara os dados extraídos para análise.
    calculate_cumulative_goals(df): Calcula os gols acumulados por jogador ao longo dos anos.
    prepare_visualization_data(df): Prepara os dados para visualização.
"""

# Documentação para o módulo visualization.plots
"""
Módulo para visualização dos dados de gols acumulados.

Funções:
    plot_cumulative_goals(data, output_file, title, subtitle): Cria um gráfico de gols acumulados.
    create_animation(data, output_file, fps, duration): Cria uma animação GIF dos gols acumulados.
"""

# Documentação para o módulo cli
"""
Módulo de interface de linha de comando para o pacote goal500.

Comandos:
    extract: Extrai dados da Wikipedia e salva em um arquivo CSV.
    plot: Cria uma visualização estática a partir de dados em CSV.
    animate: Cria uma animação GIF a partir de dados em CSV.

Uso:
    goal500 extract --output dados.csv
    goal500 plot --input dados.csv --output grafico.png
    goal500 animate --input dados.csv --output animacao.gif
"""

# Exemplo de uso do pacote
"""
Exemplo de uso do pacote goal500:

```python
import goal500
import matplotlib.pyplot as plt

# Extrair dados de jogadores
dados = goal500.get_player_stats()

# Visualizar dados
fig = goal500.plot_cumulative_goals(dados)
plt.show()

# Salvar visualização
goal500.plot_cumulative_goals(dados, output_file="gols_acumulados.png")

# Criar animação
goal500.create_animation(dados, output_file="animacao_gols.gif")
```
"""
