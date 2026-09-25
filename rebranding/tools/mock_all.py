import subprocess, sys, os
from PIL import Image
import numpy as np
S="/tmp/claude-1000/-home-user-projects-matchhold/7b41e65d-5e68-4a3d-92c6-7055445f73e0/scratchpad/"
E="env/"; I="icons/keyed/"
def load(p): return Image.open(p).convert("RGBA")
def keyed(p):  # ключ #FF00FF -> alpha (для файлов без настоящей альфы)
    out=S+"k_"+os.path.basename(p)
    if not os.path.exists(out): subprocess.run(["python3","../tools/key_layer.py",p,out],check=True)
    return load(out)
def cover(im,vw,vh):
    r=max(vw/im.width,vh/im.height); im=im.resize((int(im.width*r)+1,int(im.height*r)+1),Image.LANCZOS)
    x=(im.width-vw)//2; y=(im.height-vh)//2; return im.crop((x,y,x+vw,y+vh))
def trim(im):
    bb=im.getchannel("A").point(lambda v:255 if v>10 else 0).getbbox(); return im.crop(bb)
def sz(im,w=None,h=None):
    if w is None: w=int(im.width*h/im.height)
    if h is None: h=int(im.height*w/im.width)
    return im.resize((w,h),Image.LANCZOS)

# гнездо-сердце: полость (кремовая) в дневном кольце, заливка вписывается внутрь по центроиду
from scipy import ndimage as ndi
sock_d=load(I+"heart_socket_day_v1.png"); _a=np.array(sock_d)
_c=(_a[...,0]>205)&(_a[...,1]>190)&(_a[...,2]>150)&(_a[...,3]>200)
_c=ndi.binary_closing(_c,iterations=3); _l,_n=ndi.label(_c)
_hol=ndi.binary_fill_holes(_l==(np.argmax(ndi.sum(_c,_l,range(1,_n+1)))+1))
_hy,_hx=np.where(_hol); HC=(_hx.mean(),_hy.mean())
_f=load(I+"heart_fill_v1.png"); FILL=_f.crop(_f.getchannel("A").point(lambda v:255 if v>128 else 0).getbbox())
_fy,_fx=np.where(np.array(FILL.getchannel("A"))>128); FC=(_fx.mean(),_fy.mean())
FILL_SCALE=0.98*0.92   # ponytail: 0.98 = масштаб, при котором заливка целиком в полости; 0.92 запас

def hearts(night,n_full,n_total,size,pitch):
    sock=load(I+("heart_socket_night_v1.png" if night else "heart_socket_day_v1.png"))
    f=FILL.resize((int(FILL.width*FILL_SCALE),int(FILL.height*FILL_SCALE)),Image.LANCZOS)
    fcx=FC[0]*f.width/FILL.width; fcy=FC[1]*f.height/FILL.height
    col=Image.new("RGBA",(size,pitch*n_total),(0,0,0,0))
    for i in range(n_total):
        c=Image.new("RGBA",(512,512),(0,0,0,0)); c.alpha_composite(sock)
        if i<n_full: c.alpha_composite(f,(int(round(HC[0]-fcx)),int(round(HC[1]-fcy))))
        col.alpha_composite(sz(c,size,size),(0,i*pitch))
    return col

def magic_row(night,slot,gap,icons):
    ring=load(I+("slot_ring_night_v1.png" if night else "slot_ring_day_v1.png"))
    row=Image.new("RGBA",((slot+gap)*len(icons)-gap,slot),(0,0,0,0))
    for i,ic in enumerate(icons):
        base=Image.new("RGBA",(512,512),(0,0,0,0)); base.alpha_composite(ring)
        if ic: base.alpha_composite(sz(load(I+ic),290,290),(111,105))
        row.alpha_composite(sz(base,slot,slot),(i*(slot+gap),0))
    return row

def plank(night,width,items):
    pl=trim(load(I+("inventory_plank_night_v1.png" if night else "inventory_plank_day_v1.png")))
    W,H=pl.size; ims=Image.new("RGBA",pl.size,(0,0,0,0)); ims.alpha_composite(pl)
    for fx,it in zip((0.22,0.495,0.775),items):
        if it:
            ic=sz(load(I+it),int(H*0.62),int(H*0.62)); ims.alpha_composite(ic,(int(W*fx-ic.width/2),int(H*0.50-ic.height/2)))
    return sz(ims,width)

def plate(night,length,thick,vertical):
    pl=trim(load(I+("panel_plate_night_v1.png" if night else "panel_plate_day_v1.png")))
    W,H=pl.size; sc=thick/H; cap=int(H*0.36)          # уголок ~0.36 высоты плашки
    cw=max(1,int(cap*sc)); mid=pl.crop((cap,0,W-cap,H)).resize((length-2*cw,thick),Image.LANCZOS)
    out=Image.new("RGBA",(length,thick),(0,0,0,0))
    out.alpha_composite(sz(pl.crop((0,0,cap,H)),cw,thick),(0,0)); out.alpha_composite(mid,(cw,0))
    out.alpha_composite(sz(pl.crop((W-cap,0,W,H)),cw,thick),(length-cw,0))
    return (out.rotate(90,expand=True) if vertical else out), cw

def hearts_panel(night,thick,n_full,n_total):
    """Панель растёт с числом сердец: длина = уголки + n*шаг. Лиана фиксированного размера, при нехватке длины
    продолжается зеркальными копиями (ponytail: шов на кончиках лианы, если заметен, сделать отдельный тайл)."""
    hs=int(thick*0.74); hp=hs-2; margin=10
    cw=plate(night,3*thick,thick,True)[1]
    length=2*(cw+margin)+n_total*hp
    pn,cw=plate(night,length,thick,True)
    vine=trim(load(I+("vine_wrap_night_v1.png" if night else "vine_wrap_day_v1.png")))
    vh=int(thick*9.0); vw=int(vine.width*vh/vine.height); vine=sz(vine,vw,vh)   # размер лианы фиксирован по толщине панели
    need=int(length*1.05); strip=Image.new("RGBA",(vw,max(need,vh)),(0,0,0,0)); y=0; flip=False
    while y<strip.height:
        strip.alpha_composite(vine.transpose(Image.FLIP_TOP_BOTTOM) if flip else vine,(0,y)); y+=vh-8; flip=not flip
    strip=strip.crop((0,(strip.height-need)//2,vw,(strip.height-need)//2+need))
    pad=vw//2
    out=Image.new("RGBA",(thick+2*pad,length+need-length),(0,0,0,0))
    top=(need-length)//2
    out.alpha_composite(pn,(pad,top))
    out.alpha_composite(strip,(pad+int(thick*0.12)-vw//2,0))          # лиана вдоль левого края, под сердцами
    out.alpha_composite(hearts(night,n_full,n_total,hs,hp),(pad+(thick-hs)//2,top+cw+margin))
    return out,pad,top

def trough(night,length,width,frac):
    """Скруглённый врез с полосой опыта (без своей рамки: рамка это внешняя плашка). Рисуем в 4× и уменьшаем."""
    K=4; W,H=width*K,length*K; r=W//2
    lip=(226,182,92) if not night else (160,120,80); dark=(52,32,20) if not night else (14,18,40)
    im=Image.new("RGBA",(W,H),(0,0,0,0)); from PIL import ImageDraw
    d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,W-1,H-1],r,fill=lip+(255,))                      # светлая кромка
    d.rounded_rectangle([3*K//2,3*K//2,W-1-3*K//2,H-1-3*K//2],r-3*K//2,fill=dark+(255,))   # врез
    # внутренняя тень сверху и слева
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([3*K//2,3*K//2,W-1-3*K//2,H-1-3*K//2],r-3*K//2,fill=(0,0,0,110))
    sh=sh.transform(sh.size,Image.AFFINE,(1,0,-2*K,0,1,-2*K)); im.alpha_composite(sh)
    # заливка снизу вверх, тот же скруглённый контур с отступом
    pad=5*K; fh=int((H-2*pad)*frac)
    mask=Image.new("L",(W,H),0); ImageDraw.Draw(mask).rounded_rectangle([pad,pad,W-1-pad,H-1-pad],r-pad,fill=255)
    cut=Image.new("L",(W,H),0); ImageDraw.Draw(cut).rectangle([0,H-pad-fh,W,H],fill=255)
    from PIL import ImageChops
    mask=ImageChops.multiply(mask,cut)
    grad=Image.new("RGBA",(W,H)); gp=grad.load()
    for x in range(W):
        t=x/(W-1); c=(int(250-40*t),int(208-42*t),int(96-30*t),255)
        for y in range(H): gp[x,y]=c
    grad.putalpha(mask); im.alpha_composite(grad)
    # блик по левому краю заливки
    hl=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(hl).rounded_rectangle([pad+3*K,pad+3*K,pad+3*K+K*2,H-pad-3*K],K,fill=(255,245,200,120))
    hlm=ImageChops.multiply(hl.getchannel("A"),cut); hl.putalpha(hlm); im.alpha_composite(hl)
    return im.resize((width,length),Image.LANCZOS)

def xp_panel(night,length,thick,frac):
    pn,cw=plate(night,length,thick,True)
    tw=int(thick*0.42); tl=length-2*int(cw*1.15)
    tr=trough(night,tl,tw,frac)
    pn.alpha_composite(tr,((thick-tw)//2,(length-tl)//2)); return pn


# ---------- инвентарь: плашка + кольца + заряды ----------
LOOT={"healthPotion":("loot_health_potion_v1.png",3),"manaPotion":("loot_mana_potion_v1.png",3),"bomb":("loot_bomb_v1.png",3),
      "equipment":("loot_equipment_v1.png",3),"callDragon":("loot_dragon_scroll_v1.png",1)}   # max зарядов как в loot.js: 3, у large 1

def bead(night,full,d):
    """Кружок заряда: латунный/железный ободок, полный = золотой, пустой = тёмный врез (рисуем 8× и уменьшаем)."""
    K=8; D=d*K; im=Image.new("RGBA",(D,D),(0,0,0,0)); from PIL import ImageDraw
    dr=ImageDraw.Draw(im); rim=(196,150,58) if not night else (120,110,140)
    dr.ellipse([0,0,D-1,D-1],fill=rim+(255,))
    q=int(D*0.14)
    if full:
        for i in range(D//2-q,0,-1):
            t=i/(D//2-q); c=(int(255-40*t),int(232-84*t),int(140-96*t))   # блик в центре -> насыщенное золото к краю
            dr.ellipse([D//2-i,D//2-i,D//2+i,D//2+i],fill=c+(255,))
        dr.ellipse([int(D*0.28),int(D*0.22),int(D*0.46),int(D*0.38)],fill=(255,250,220,200))
    else:
        dr.ellipse([q,q,D-1-q,D-1-q],fill=(46,28,16,255) if not night else (12,14,32,255))
        dr.ellipse([q+K,q+K*2,D-1-q-K,D-1-q],fill=(70,44,26,255) if not night else (24,28,56,255))
    return im.resize((d,d),Image.LANCZOS)

def ring_art(night):
    pl=trim(load(I+("inventory_plank_night_v1.png" if night else "inventory_plank_day_v1.png"))); W,H=pl.size
    cx,cy,r=int(W*0.495),H//2,int(H*0.44)
    ring=pl.crop((cx-r,cy-r,cx+r,cy+r)); m=Image.new("L",ring.size,0)
    from PIL import ImageDraw; ImageDraw.Draw(m).ellipse([0,0,ring.width-1,ring.height-1],fill=255)
    ring.putalpha(ImageChops_multiply(ring.getchannel("A"),m)); return ring
def ImageChops_multiply(a,b):
    from PIL import ImageChops; return ImageChops.multiply(a,b)

def inventory_panel(night,thick,items):
    """items: список (имя предмета, число зарядов). Длина = уголки + n*шаг."""
    n=len(items); d=int(thick*0.70); pitch=int(d*1.18); margin=8
    cw=plate(night,3*thick,thick,False)[1]; length=2*(cw+margin)+n*pitch
    pn,cw=plate(night,length,thick,False); ring=sz(ring_art(night),d,d)
    for i,(name,ch) in enumerate(items):
        fn,mx=LOOT[name]; cx=cw+margin+i*pitch+pitch//2; cy=thick//2-int(thick*0.06)
        pn.alpha_composite(ring,(cx-d//2,cy-d//2))
        pn.alpha_composite(sz(load(I+fn),int(d*0.62),int(d*0.62)),(cx-int(d*0.31),cy-int(d*0.31)))
        bd=max(6,int(d*0.20)); R=d/2
        if mx==1: pos=[(0,R*1.02)]
        else: pos=[(-R*0.62,R*0.80),(0,R*1.05),(R*0.62,R*0.80)]
        for j,(dx,dy) in enumerate(pos):
            pn.alpha_composite(bead(night,j<ch,bd),(int(cx+dx-bd/2),int(cy+dy-bd/2)))
    return pn

def board(night,F):
    fr=load(E+("frame/frame_night_thin_fit.png" if night else "frame/frame_day_thin_fit.png"))
    fl=load(E+("floor/floor_night_v2.png" if night else "floor/floor_day_v2.png"))
    sk=keyed(E+("floor/socket_night_v2.png" if night else "floor/socket_day_v3_2.png"))
    o=int(182/2048*F); ob=F-2*o
    b=Image.new("RGBA",(F,F),(0,0,0,0)); b.paste(fl.resize((ob,ob)),(o,o))
    # ячейка = лунка без прозрачных полей; отступ от бортика m прежний, зазор между лунками тоже m
    skt=sk.crop(sk.getchannel("A").point(lambda v:255 if v>200 else 0).getbbox())
    g=0.05*ob/8                      # зазор между лунками = отступ от бортика
    s=int(round((ob-9*g)/8)); m=(ob-8*s)/9
    lun=skt.resize((s,s),Image.LANCZOS)
    for i in range(8):
        for j in range(8): b.alpha_composite(lun,(o+int(round(m+i*(s+m))),o+int(round(m+j*(s+m)))))
    b.alpha_composite(fr.resize((F,F),Image.LANCZOS)); return b,o,ob

STAGE=1
def layers(night,port,vw,vh):
    t="night" if night else "day"
    if not port:
        v=cover(load(E+f"bg/bg_s{STAGE}_far_{t}_land_v1.png"),vw,vh)
        v.alpha_composite(cover(keyed(E+f"bg/bg_s{STAGE}_mid_{t}_land_v1.png"),vw,vh))
        fg=cover(load(E+("fg/fg_day_land_v3.png" if not night else "fg/fg_night_land_v2.png")),vw,vh)
    else:
        v=cover(load(E+f"bg/bg_s{STAGE}_far_{t}_port_v1.png"),vw,vh)
        v.alpha_composite(cover(load(E+f"bg/bg_s{STAGE}_mid_{t}_port_"+("v2" if (STAGE==3 and not night) else "v1")+".png"),vw,vh))
        fg=cover(load(E+("fg/fg_day_port_v4_a.png" if not night else "fg/fg_night_port_v3_a.png")),vw,vh)
    return v,fg

ICONS=["spell_haste_v1.png","spell_freeze_time_v1.png","spell_phase_change_v1.png",None]
POTS=[]
ITEMS=[("healthPotion",3),("manaPotion",2),("bomb",1),("equipment",3),("callDragon",1)]

def desktop(night):
    vw,vh=1920,1080; v,fg=layers(night,False,vw,vh)
    k=1.32; B=int(480*k); F=int(B*2048/1684); b,o,ob=board(night,F)
    strip=int(110*k); hud=84; total=strip+F+hud; y0=(vh-total)//2
    xF=(vw-F)//2; yF=y0+strip-12
    v.alpha_composite(b,(xF,yF)); v.alpha_composite(fg)     # интерфейс поверх переднего слоя
    yo=yF+o; xo=xF+o
    # сердца слева от доски, опыт справа
    edge=int(32/2048*F)
    thick=84                                      # одна толщина для панелей сердец, опыта и инвентаря
    hp_,pad,top=hearts_panel(night,thick,6,9)
    v.alpha_composite(hp_,(xF+edge-thick-6-pad,yo-top))
    v.alpha_composite(xp_panel(night,B,thick,0.6),(xF+F-edge+6,yo))
    # низ: магия слева, инвентарь справа
    yb=yF+F-edge+2                                # сразу под нижним рельсом рамки
    m=magic_row(night,int(thick*0.70),10,ICONS); v.alpha_composite(m,(xF+edge,yb+(thick-m.height)//2))
    inv=inventory_panel(night,thick,ITEMS); v.alpha_composite(inv,(xF+F-edge-inv.width,yb))
    return v.convert("RGB")

def portrait(night):
    vw,vh=390,844; v,fg=layers(night,True,vw,vh)
    F=int(vw-2*4); B=int(F*1684/2048); b,o,ob=board(night,F)
    strip=int(110*B/560); hud=50; total=strip+F+hud; y0=(vh-total)//2
    xF=(vw-F)//2; yF=y0+strip-4
    v.alpha_composite(b,(xF,yF)); v.alpha_composite(fg); yo=yF+o
    edge=int(32/2048*F); rail=o-edge
    hs=rail-2; hp=hs-1; hc=hearts(night,6,9,hs,hp); v.alpha_composite(hc,(xF+edge+(rail-hs)//2,yo+8))
    tw=max(8,int(rail*0.62)); xp=trough(night,ob-16,tw,0.6); v.alpha_composite(xp,(xF+o+ob+(rail-tw)//2,yo+8))   # врез прямо на рельсе, без своей рамки
    yb=yF+F-edge+2
    m=magic_row(night,32,4,ICONS); v.alpha_composite(m,(xF+edge,yb+(44-m.height)//2))
    inv=inventory_panel(night,44,ITEMS[:4]); v.alpha_composite(inv,(xF+F-edge-inv.width,yb))
    return v.convert("RGB")

def growth(night):
    thick=int(70*3.9*trim(load(I+("inventory_plank_night_v1.png" if night else "inventory_plank_day_v1.png"))).size[1]/trim(load(I+("inventory_plank_night_v1.png" if night else "inventory_plank_day_v1.png"))).size[0])
    ims=[hearts_panel(night,thick,f,n)[0] for f,n in ((2,3),(6,9),(10,14))]
    H=max(i.height for i in ims); W=sum(i.width for i in ims)+40
    bg=Image.new("RGBA",(W,H),(120,150,180,255) if not night else (25,35,80,255)); x=0
    for i in ims: bg.alpha_composite(i,(x,0)); x+=i.width+20
    return bg.convert("RGB")

def inv_growth(night):
    thick=84; pans=[inventory_panel(night,thick,ITEMS[:k]) for k in range(1,6)]
    W=max(p.width for p in pans)+20; H=sum(p.height for p in pans)+10*5
    bg=Image.new("RGBA",(W,H),(120,150,180,255) if not night else (25,35,80,255)); y=5
    for p in pans: bg.alpha_composite(p,(10,y)); y+=p.height+10
    return bg.convert("RGB")

if __name__=="__main__":
    global_out={}
    growth(False).save("env/mock_hearts_growth_day.png"); growth(True).save("env/mock_hearts_growth_night.png")
    inv_growth(False).save("env/mock_inventory_growth_day.png"); inv_growth(True).save("env/mock_inventory_growth_night.png")
    for st in (1,2,3,4):
        STAGE=st
        for n in (False,True):
            global_out[(st,"d",n)]=desktop(n); global_out[(st,"p",n)]=portrait(n)
    for n in (False,True):
        t="night" if n else "day"
        global_out[(1,"d",n)].save(f"env/mock_all_desktop_{t}.png"); global_out[(1,"p",n)].save(f"env/mock_all_portrait_{t}.png")
    # обзор этапов: десктоп 2 колонки (день, ночь) × 4 строки; портрет 8 в ряд
    sd=Image.new("RGB",(960*2+10,4*(540+6)),(30,30,30)); sp=Image.new("RGB",(8*(390+6),844),(30,30,30))
    for i,st in enumerate((1,2,3,4)):
        for j,n in enumerate((False,True)):
            sd.paste(global_out[(st,"d",n)].resize((960,540)),(j*970,i*546))
            sp.paste(global_out[(st,"p",n)],((i*2+j)*396,0))
    sd.save("env/mock_stages_desktop.png"); sp.save("env/mock_stages_portrait.png")
