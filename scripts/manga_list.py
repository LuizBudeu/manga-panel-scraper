import json 


a = [(100*i, 100*(i+1)) for i in range(0, 4)]


for i in a:
    with open(fr"D:\User\VS_Code_testes\python\WebScraping\manga_panels\scripts\data\top{i[0]}_{i[1]}manga.json", "r") as f:
        data = json.load(f)
        
    with open('mangalist.txt', 'a') as f:
        for j in data['data']:
            f.write(f"\"{j['node']['title']}\"" + ',\n')
