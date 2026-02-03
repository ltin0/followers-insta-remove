from instagrapi import Client
import time
import random
import json
from datetime import datetime

USERNAME = ''
PASSWORD = ''

MAX_UNFOLLOWS = 500

def main():
    cl = Client()
    
    # Lista para armazenar os usuários removidos
    removed_users = []

    try:
        print("Tentando logar...")
        cl.login(USERNAME, PASSWORD)
        print("Login realizado com sucesso!")
    except Exception as e:
        print(f"Erro no login: {e}")
        # Adiciona a impressão do último JSON de resposta para mais detalhes
        if hasattr(cl, 'last_json'):
            print(f"Detalhes do erro: {cl.last_json}")
        return

    user_id = cl.user_id_from_username(USERNAME)

    print("Baixando lista de seguidores (isso pode demorar)...")
    followers = cl.user_followers(user_id)

    print("Baixando lista de quem você segue...")
    following = cl.user_following(user_id)

    followers_ids = set(followers.keys())
    following_ids = set(following.keys())

    not_following_back = following_ids - followers_ids

    print(f"Total de seguidores: {len(followers_ids)}")
    print(f"Total seguindo: {len(following_ids)}")
    print(f"Pessoas que não te seguem de volta: {len(not_following_back)}")

    count = 0

    print("\n--- Iniciando Processo de Unfollow ---")

    for user_target_id in not_following_back:
        if count >= MAX_UNFOLLOWS:
            print(f"Limite de segurança ({MAX_UNFOLLOWS}) atingido. Parando por hoje.")
            break

        user_info = following[user_target_id]
        print(f"Deixando de seguir: {user_info.username}...")

        try:
            cl.user_unfollow(user_target_id)
            count += 1
            
            # Adiciona o usuário removido à lista
            removed_users.append({
                'username': user_info.username,
                'user_id': user_target_id,
                'full_name': user_info.full_name if hasattr(user_info, 'full_name') else '',
                'removed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            sleep_time = random.randint(30, 60)
            print(f"Aguardando {sleep_time} segundos para a próxima ação...")
            time.sleep(sleep_time)

        except Exception as e:
            print(f"Erro ao tentar deixar de seguir: {e}")
            time.sleep(60)

    # Salva a lista de usuários removidos em um arquivo JSON
    if removed_users:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'removed_followers_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'total_removed': len(removed_users),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'removed_users': removed_users
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Lista de {len(removed_users)} usuários removidos salva em: {filename}")
    else:
        print("\nNenhum usuário foi removido nesta execução.")

    print("Processo finalizado.")

if __name__ == "__main__":
    main()