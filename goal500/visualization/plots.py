"""
Módulo para visualização dos dados de gols acumulados.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import imageio
import os
from matplotlib.ticker import MaxNLocator

from goal500.utils.data_processing import prepare_visualization_data


def plot_cumulative_goals(data, output_file=None, title="Cumulative goals", subtitle="Active players with most goals"):
    """
    Cria um gráfico de gols acumulados por anos ativos.
    
    Args:
        data (pd.DataFrame): DataFrame com os dados extraídos.
        output_file (str, optional): Caminho para salvar o gráfico. Se None, apenas exibe.
        title (str, optional): Título do gráfico.
        subtitle (str, optional): Subtítulo do gráfico.
        
    Returns:
        matplotlib.figure.Figure: Objeto figura do matplotlib.
    """
    # Preparar dados para visualização
    plot_data = prepare_visualization_data(data)
    
    if plot_data.empty:
        print("Sem dados para visualizar.")
        return None
    
    # Criar figura
    plt.figure(figsize=(12, 8))
    
    # Criar um colormap personalizado baseado no viridis
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(plot_data["name"].unique())))
    
    # Plotar dados para cada jogador
    for i, (name, group) in enumerate(plot_data.groupby("name")):
        plt.plot(group["years_active"], group["cumulative_goals"], 
                 marker="o", markersize=5, linewidth=2, 
                 color=colors[i], label=group["player_label"].iloc[0])
        
        # Adicionar rótulo no último ponto
        last_point = group.iloc[-1]
        plt.text(last_point["years_active"], last_point["cumulative_goals"], 
                 last_point["player_label"], fontsize=10)
    
    # Configurar eixos
    plt.xlabel("Anos ativos", fontsize=12)
    plt.ylabel("Gols", fontsize=12)
    
    # Configurar ticks dos eixos
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    
    # Adicionar grade
    plt.grid(True, linestyle="--", alpha=0.7)
    
    # Adicionar título e subtítulo
    plt.title(f"{title}\n{subtitle}", fontsize=16)
    
    # Adicionar fonte
    plt.figtext(0.5, 0.01, "Fonte: Wikipedia", ha="center", fontsize=10)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Salvar ou exibir
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Gráfico salvo em: {output_file}")
    
    return plt.gcf()


def create_animation(data, output_file="animation.gif", fps=2, duration=5):
    """
    Cria uma animação GIF dos gols acumulados ao longo dos anos.
    
    Args:
        data (pd.DataFrame): DataFrame com os dados extraídos.
        output_file (str, optional): Caminho para salvar a animação.
        fps (int, optional): Frames por segundo.
        duration (int, optional): Duração em segundos da pausa no final.
        
    Returns:
        str: Caminho do arquivo GIF criado.
    """
    # Preparar dados para visualização
    plot_data = prepare_visualization_data(data)
    
    if plot_data.empty:
        print("Sem dados para visualizar.")
        return None
    
    # Criar diretório temporário para os frames
    temp_dir = "temp_frames"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Obter anos únicos
    years_active = sorted(plot_data["years_active"].unique())
    
    # Criar um colormap personalizado baseado no viridis
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(plot_data["name"].unique())))
    
    # Criar frames
    frames = []
    
    for i, year in enumerate(years_active):
        # Filtrar dados até o ano atual
        current_data = plot_data[plot_data["years_active"] <= year]
        
        # Criar figura
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plotar dados para cada jogador
        for j, (name, group) in enumerate(current_data.groupby("name")):
            # Filtrar grupo até o ano atual
            group = group[group["years_active"] <= year]
            
            if not group.empty:
                ax.plot(group["years_active"], group["cumulative_goals"], 
                        marker="o", markersize=5, linewidth=2, 
                        color=colors[j], label=group["player_label"].iloc[0])
                
                # Adicionar rótulo no último ponto
                last_point = group.iloc[-1]
                ax.text(last_point["years_active"], last_point["cumulative_goals"], 
                        last_point["player_label"], fontsize=10)
        
        # Configurar eixos
        ax.set_xlabel("Anos ativos", fontsize=12)
        ax.set_ylabel("Gols", fontsize=12)
        
        # Configurar limites dos eixos
        ax.set_xlim(0, max(years_active) + 1)
        ax.set_ylim(0, plot_data["cumulative_goals"].max() * 1.1)
        
        # Configurar ticks dos eixos
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        
        # Adicionar grade
        ax.grid(True, linestyle="--", alpha=0.7)
        
        # Adicionar título e subtítulo
        ax.set_title(f"Gols acumulados\nJogadores ativos com mais gols (Ano ativo: {year})", fontsize=16)
        
        # Adicionar fonte
        plt.figtext(0.5, 0.01, "Fonte: Wikipedia", ha="center", fontsize=10)
        
        # Ajustar layout
        plt.tight_layout()
        
        # Salvar frame
        frame_file = f"{temp_dir}/frame_{i:03d}.png"
        plt.savefig(frame_file, dpi=100, bbox_inches="tight")
        frames.append(frame_file)
        
        plt.close(fig)
    
    # Adicionar frames extras no final para pausa
    last_frame = frames[-1]
    for _ in range(fps * duration):
        frames.append(last_frame)
    
    # Criar GIF
    with imageio.get_writer(output_file, mode="I", fps=fps) as writer:
        for frame in frames:
            image = imageio.imread(frame)
            writer.append_data(image)
    
    # Limpar frames temporários
    for frame in set(frames):
        os.remove(frame)
    os.rmdir(temp_dir)
    
    print(f"Animação salva em: {output_file}")
    return output_file
