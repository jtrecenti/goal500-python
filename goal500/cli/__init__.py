"""
Módulo de interface de linha de comando para o pacote goal500.
"""

import argparse
import sys
import pandas as pd

from goal500.scrapers.wikipedia import get_player_stats
from goal500.visualization.plots import plot_cumulative_goals, create_animation


def main():
    """
    Função principal da interface de linha de comando.
    """
    parser = argparse.ArgumentParser(
        description="Extrai e visualiza dados de gols acumulados de jogadores de futebol."
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Comando extract
    extract_parser = subparsers.add_parser("extract", help="Extrai dados da Wikipedia")
    extract_parser.add_argument(
        "--output", "-o", 
        help="Arquivo CSV para salvar os dados extraídos",
        default="player_stats.csv"
    )
    
    # Comando plot
    plot_parser = subparsers.add_parser("plot", help="Cria visualização dos dados")
    plot_parser.add_argument(
        "--input", "-i", 
        help="Arquivo CSV com os dados extraídos",
        default="player_stats.csv"
    )
    plot_parser.add_argument(
        "--output", "-o", 
        help="Arquivo para salvar a visualização",
        default="cumulative_goals.png"
    )
    plot_parser.add_argument(
        "--title", "-t", 
        help="Título do gráfico",
        default="Cumulative goals"
    )
    plot_parser.add_argument(
        "--subtitle", "-s", 
        help="Subtítulo do gráfico",
        default="Active players with most goals"
    )
    
    # Comando animate
    animate_parser = subparsers.add_parser("animate", help="Cria animação dos dados")
    animate_parser.add_argument(
        "--input", "-i", 
        help="Arquivo CSV com os dados extraídos",
        default="player_stats.csv"
    )
    animate_parser.add_argument(
        "--output", "-o", 
        help="Arquivo GIF para salvar a animação",
        default="cumulative_goals.gif"
    )
    animate_parser.add_argument(
        "--fps", 
        help="Frames por segundo",
        type=int,
        default=2
    )
    animate_parser.add_argument(
        "--duration", 
        help="Duração em segundos da pausa no final",
        type=int,
        default=5
    )
    
    args = parser.parse_args()
    
    if args.command == "extract":
        print("Extraindo dados da Wikipedia...")
        data = get_player_stats()
        data.to_csv(args.output, index=False)
        print(f"Dados salvos em: {args.output}")
        
    elif args.command == "plot":
        print(f"Criando visualização a partir de: {args.input}")
        try:
            data = pd.read_csv(args.input)
            plot_cumulative_goals(data, args.output, args.title, args.subtitle)
        except FileNotFoundError:
            print(f"Erro: Arquivo {args.input} não encontrado.")
            sys.exit(1)
            
    elif args.command == "animate":
        print(f"Criando animação a partir de: {args.input}")
        try:
            data = pd.read_csv(args.input)
            create_animation(data, args.output, args.fps, args.duration)
        except FileNotFoundError:
            print(f"Erro: Arquivo {args.input} não encontrado.")
            sys.exit(1)
            
    else:
        parser.print_help()
        

if __name__ == "__main__":
    main()
