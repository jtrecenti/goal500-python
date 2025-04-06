"""
Módulo para processamento e manipulação de dados extraídos.
"""

import pandas as pd
import numpy as np


def clean_data(df):
    """
    Limpa e prepara os dados extraídos para análise.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados extraídos.
        
    Returns:
        pd.DataFrame: DataFrame limpo e preparado.
    """
    if df.empty:
        return df
        
    # Converter ano para numérico
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    
    # Remover linhas com ano inválido
    df = df.dropna(subset=["year"])
    
    # Converter total para numérico
    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    
    # Remover linhas com total inválido
    df = df.dropna(subset=["total"])
    
    return df


def calculate_cumulative_goals(df):
    """
    Calcula os gols acumulados por jogador ao longo dos anos.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados limpos.
        
    Returns:
        pd.DataFrame: DataFrame com gols acumulados.
    """
    if df.empty:
        return df
        
    # Agrupar por jogador e ano, somando os gols
    yearly_goals = df.groupby(["name", "year"])["total"].sum().reset_index()
    
    # Ordenar por jogador e ano
    yearly_goals = yearly_goals.sort_values(["name", "year"])
    
    # Calcular gols acumulados para cada jogador
    result = []
    
    for name, group in yearly_goals.groupby("name"):
        # Ordenar por ano
        group = group.sort_values("year")
        
        # Calcular anos ativos (diferença entre o primeiro ano e o atual)
        group["years_active"] = group["year"] - group["year"].min()
        
        # Calcular gols acumulados
        group["cumulative_goals"] = group["total"].cumsum()
        
        # Calcular total de gols do jogador
        total_goals = group["total"].sum()
        
        # Adicionar nome com total de gols entre parênteses
        group["player_label"] = f"{name} ({total_goals})"
        
        result.append(group)
    
    if result:
        return pd.concat(result, ignore_index=True)
    else:
        return pd.DataFrame(columns=["name", "year", "total", "years_active", "cumulative_goals", "player_label"])


def prepare_visualization_data(df):
    """
    Prepara os dados para visualização.
    
    Args:
        df (pd.DataFrame): DataFrame com os dados limpos.
        
    Returns:
        pd.DataFrame: DataFrame preparado para visualização.
    """
    if df.empty:
        return df
        
    # Limpar dados
    clean_df = clean_data(df)
    
    # Calcular gols acumulados
    cumulative_df = calculate_cumulative_goals(clean_df)
    
    return cumulative_df
