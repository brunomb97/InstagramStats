import instaloader
import os
import argparse

from datetime import date

parser = argparse.ArgumentParser(description='Adventure')
parser.add_argument('profile', type=str, help='Perfil a evaluar')
parser.add_argument('--login', type=str, help='Sesión de usuario', required=True)
parser.add_argument('--get-stats', type=str, help='Perfiles de interés para obtener estadisticas individuales', nargs='*')
args = parser.parse_args()

PROFILE = args.profile
USER = args.login
USERS = args.get_stats

def url(shortcode):
    return f'https://www.instagram.com/p/{shortcode}/'
    
def print_comment(owner, comment):
    owner = owner.username
    string = '\t\t' + owner + ': ' + comment.split('\n')[0] + '\n'
    comment = comment.split('\n')[1:]
    for line in comment:
        string += '\t\t' + len(owner+': ')*' ' + line + '\n'
    return string

def print_subcomment(owner1, owner2, comment):
    owner1 = owner1.username
    owner2 = owner2.username
    string = '\t\t' + len(owner1+': ')*' ' + owner2 + ': ' + comment.split('\n')[0] + '\n'
    comment = comment.split('\n')[1:]
    for line in comment:
        string += '\t\t' + len(owner1+owner2+2*': ')*' ' + line + '\n'
    return string

date = date.today().isoformat()
L = instaloader.Instaloader()

# Load session previously saved with `instaloader -l USERNAME`:
print('Iniciando sesión como {}.'.format(USER))
L.load_session_from_file(USER)

print('Detectando usuarios de interés.')
USERS_TO_FIND = [instaloader.Profile.from_username(L.context, u) for u in USERS]

print('Realizando lectura sobre {}.'.format(PROFILE))
profile = instaloader.Profile.from_username(L.context, PROFILE)

print("Obteniendo información de las publicaciones de {}.".format(profile.username))

likes = {user: 0 for user in profile.get_followers()}
user_likes = {user: [] for user in USERS_TO_FIND}
user_nolikes = {user: [] for user in USERS_TO_FIND}

comments = likes.copy()
user_comments = {user: [] for user in USERS_TO_FIND}
user_nocomments = {user: [] for user in USERS_TO_FIND}
user_textcomments = {user: {} for user in USERS_TO_FIND}

try:
    os.makedirs(f'{PROFILE}')
except Exception:
    pass

try:
    os.makedirs(os.path.join(f'{PROFILE}',f'{date}'))
except Exception:
    pass

try:
    os.makedirs(os.path.join(f'{PROFILE}',f'{date}',f'users'))
except Exception:
    pass

fp = open(os.path.join(f'{PROFILE}',f'{date}','posts.txt'),'w')

print(f'Fecha: {date}', file=fp)
print(f'ID: {profile.userid}', file=fp)
print(f'Nombre: {profile.username}', file=fp)
print(f'Publicaciones: {profile.mediacount}', file=fp)
print(f'IGTV: {profile.igtvcount}', file=fp)
print(f'Seguidores: {profile.followers}', file=fp)
print(f'Seguidos: {profile.followees}', file=fp)
print(f'Biografia:', file=fp)
print(f'{profile.biography}', file=fp)
print('\n\n', file=fp)

print('')

n = profile.mediacount
l = len(str(profile.mediacount))
text_post = []

for post in profile.get_posts():
    
    text_post.append('')
    print(f'{n}'.rjust(l, '0')+f'. {url(post.shortcode)}')
    print(post.date_local)
    
    text_post[-1] += f'{n}'.rjust(l, '0') + f'. {url(post.shortcode)}' + '\n'
    text_post[-1] += f'{post.date_local}' + '\n'
    if post.caption:
        text_post[-1] += post.caption + '\n'
    text_post[-1] += '\n'
    
    post_likes = list(post.get_likes())
    for user in post_likes:
        if user not in likes:
            likes[user] = 0
        likes[user] += 1
    
    text_post[-1] += f'\tComentarios:' + '\n\n'
    
    post_comments = []
    
    for comment in post.get_comments():
        post_comments.append(comment)
        text_post[-1] += print_comment(comment.owner, comment.text) + '\n'
        
        if comment.owner not in comments:
            comments[comment.owner] = 0
        comments[comment.owner] += 1
        
        if comment.owner in USERS_TO_FIND:
            if post not in user_textcomments[comment.owner]:
                user_textcomments[comment.owner][post] = []
            user_textcomments[comment.owner][post].append(print_comment(comment.owner, comment.text))
            
        for answer in comment.answers:
            post_comments.append(answer)
            text_post[-1] += print_subcomment(comment.owner, answer.owner, answer.text) + '\n'
            
            if answer.owner not in comments:
                comments[answer.owner] = 0
            comments[answer.owner] += 1

            if answer.owner in USERS_TO_FIND:
                if post not in user_textcomments[answer.owner]:
                    user_textcomments[answer.owner][post] = []
                user_textcomments[answer.owner][post].append(print_comment(answer.owner, answer.text))
        
        text_post[-1] += '\n'
    
    post_unique_comments = set([i.owner for i in post_comments])
    
    for u in USERS_TO_FIND:
        if u in post_likes:
            user_likes[u].append(post)
            print(f'✅{u.username} SI ha dado like al post', url(post.shortcode))
        else:
            user_nolikes[u].append(post)
            print(f'❌{u.username} NO ha dado like al post', url(post.shortcode))
            
        if u in post_unique_comments:
            user_comments[u].append(post)
            print(f'✅{u.username} SI ha comentado en el post', url(post.shortcode))
        else:
            user_nocomments[u].append(post)
            print(f'❌{u.username} NO ha comentado en el post', url(post.shortcode))
    
    text_post[-1] += f'\n\n\n'
    print('\n')
    
    n -= 1

text_post.reverse()
for post in text_post:
    fp.write(post)
fp.close()

print(f'Ordenando y guardando likes sobre {PROFILE}.')
likes = sorted(list(likes.items()), key=lambda i: i[1], reverse=True)

with open(os.path.join(f'{PROFILE}', f'{date}', 'likes.txt'), 'w') as f:
    print(f'Número de posts: {profile.mediacount}\n', file=f)
    for user, i in likes:
        print(f'\t{user.username}: {i}', file=f)
        
print(f'Ordenando y guardando comentarios sobre {PROFILE}.')
comments = sorted(list(comments.items()), key=lambda i: i[1], reverse=True)

with open(os.path.join(f'{PROFILE}', f'{date}', 'comments.txt'), 'w') as f:
    print(f'Número de posts: {profile.mediacount}\n', file=f)
    for user, i in comments:
        print(f'\t{user.username}: {i}', file=f)

for u in USERS_TO_FIND:
    print(f'Guardando información de {u.username} sobre {PROFILE}')
    
    with open(os.path.join(f'{PROFILE}', f'{date}', f'users', f'{u.username}.txt'), 'w') as f:
        print(f'Fecha: {date}', file=f)
        print(f'ID: {u.userid}', file=f)
        print(f'Nombre: {u.username}', file=f)
        print(f'Número de publicaciones de {PROFILE}: {profile.mediacount}', file=f)
        
        print('', file=f)
        print(f'Número de likes: {len(user_likes[u])}', file=f)
        print(f'Número de no likes: {profile.mediacount-len(user_likes[u])}', file=f)
        print(f'Número de comentarios: {len(user_textcomments[u])}', file=f)
        print(f'Número de publicaciones con comentarios: {len(user_comments[u])}', file=f)
        print(f'Número de publicaciones sin comentarios: {len(user_nocomments[u])}', file=f)
        
        print(f'Likes de {u.username}\n', file=f)
        user_likes[u] = sorted(user_likes[u], key=lambda i: i.date_local)
        for post in user_likes[u]:
            print(f'\t{post.date_local}: {url(post.shortcode)}', file=f)
        print('\n\n', file=f)
        
        print(f'No likes de {u.username}\n', file=f)
        user_nolikes[u] = sorted(user_nolikes[u], key=lambda i: i.date_local)
        for post in user_nolikes[u]:
            print(f'\t{post.date_local}: {url(post.shortcode)}', file=f)
        print('\n\n', file=f)
        
        print(f'Comentarios de {u.username}\n', file=f)
        aux_user_comments = sorted([(post, user_textcomments[u][post]) for post in user_textcomments[u]], key=lambda i: i[0].date_local)
        for post, list_comments in aux_user_comments:
            print(f'\t{post.date_local}: {url(post.shortcode) :}', file=f)
            for postcomment in list_comments:
                print(f'\t----{postcomment[:-1]}', file=f)
        print('\n\n', file=f)
        
        print(f'No comentarios de {u.username}\n', file=f)
        user_nocomments[u] = sorted(user_nocomments[u], key=lambda i: i.date_local)
        for post in user_nocomments[u]:
            print(f'\t{post.date_local}: {url(post.shortcode)}', file=f)
