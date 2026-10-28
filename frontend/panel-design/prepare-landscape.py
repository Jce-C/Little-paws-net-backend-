"""Ampliación convencional del recurso suministrado: sin generación de imágenes."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import json
root=Path(__file__).resolve().parents[2]
folder=root/'demos/panel-editorial/static/acceso'
original=Image.open(folder/'paisaje.png').convert('RGBA')
rgb=original.convert('RGB')
rgb=ImageEnhance.Contrast(rgb).enhance(.88)
rgb=ImageEnhance.Color(rgb).enhance(.84)
rgb=ImageEnhance.Brightness(rgb).enhance(1.035)
rgb.putalpha(original.getchannel('A'))
outputs=[]
for width in (768,1536,2304):
    size=(width,round(original.height*width/original.width))
    image=rgb.resize(size,Image.Resampling.LANCZOS)
    if width>768:
        alpha=image.getchannel('A')
        image=image.filter(ImageFilter.UnsharpMask(radius=.8,percent=20,threshold=3))
        image.putalpha(alpha)
    target=folder/f'paisaje-{width}.webp'
    image.save(target,'WEBP',quality=90,method=6,exact=True)
    outputs.append({'file':target.name,'width':width,'height':size[1],'bytes':target.stat().st_size})
    if width==2304:
        png=folder/'paisaje-hd.png';image.save(png,optimize=True)
        outputs.append({'file':png.name,'width':width,'height':size[1],'bytes':png.stat().st_size})
        # El acceso tiene su propia escena, sin el cielo transparente de la portada.
        top=max(0,image.getchannel('A').getbbox()[1]-24)
        scene=image.crop((0,top,image.width,image.height))
        for scene_width in (768,1536,2304):
            frame=scene.resize((scene_width,round(scene.height*scene_width/scene.width)),Image.Resampling.LANCZOS)
            target=folder/f'escena-{scene_width}.webp'
            frame.save(target,'WEBP',quality=90,method=6,exact=True)
            outputs.append({'file':target.name,'width':frame.width,'height':frame.height,'bytes':target.stat().st_size})
report={'source':{'width':original.width,'height':original.height},'method':'Lanczos, ampliación convencional sin nuevo detalle; contraste .88, saturación .84, brillo 1.035','outputs':outputs}
report_file=root/'output/login-refinado/recursos.json'
report_file.parent.mkdir(parents=True,exist_ok=True)
report_file.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
