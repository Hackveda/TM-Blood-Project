from reportlab.pdfgen import canvas
import pickle
from reportlab.lib import pdfencrypt
from django.conf import settings
from .models import Label

color_di={}

def hex_to_rgb(value):
    if(value.lower()=='#ff0000' or value.lower()=='ff0000'): #Red
        return (255/255,100/255,100/255)
    elif (value.lower()=='#ffff00' or value.lower()=='ffff00'): #Yellow
        return (255/255,192/255,0/255)
    elif (value.lower()=='#fe2e2e' or value.lower()=='fe2e2e'):#Pale_Yellow
        return(251/255,180/255,120/255)
    elif (value.lower()=='#82fa58' or value.lower()=='82fa58'): #Pale_Green
        return(146/255,208/255,80/255)
    elif (value.lower()=='#31b404' or value.lower()=='31b404'): #Green
        return(155/255,205/255,102/255)
    elif (value.lower()=='#800000' or value.lower()=='800000'): #Maroon
        return(255/255,100/255,100/255)
    if(value==''):
        value='b7dEE8'
    value = value.lstrip('#')
    lv = len(value)
    ans = tuple((int(value[i:i + lv // 3], 16))/255 for i in range(0, lv, lv // 3))

    if ans==(1,1,1):
        color_di[value]=ans
        return hex_to_rgb('')
    color_di[value]=ans
    return ans

BGCOLOR=hex_to_rgb('#E5E5E5')
SHADOW=hex_to_rgb('#cfcccc')

# 742,595


def extract(data):
    new_data={}
    dates=[data['documents'][str(5-i)]['uploaded_at'] for i in range(len(data['documents'])-2)]
    for i in range(len(dates)):
        dates[i]=dates[i][:10]
    for key in data:
        if key=='documents':
            continue
        try:
            new_data[data[key][str(5)]['category']]
        except:
            new_data[data[key][str(5)]['category']]=[]
        new_dict={'label':key,'remark':data[key][str(5-i)]['remark'],'color':[hex_to_rgb(data[key][str(5-i)]['remark_color']) for i in range(len(data[key]))],'values':[data[key][str(5-i)]['value'] for i in range(len(data[key]))]}
        new_dict['comment_color']=data[key][str(5)]['remark_color']
        new_data[data[key][str(5)]['category']].append(new_dict)
    return new_data,dates



# 742,595
# New variables
HEADER_END = 140
FOOTER_START = 720

NAME_TAG_HEIGHT = 60
NAME_TAG_RADIUS = 10
NAME_TAG_WIDTH = 215
NAME_TAG_COLOR = hex_to_rgb("F3EBEB")
NAME_TAG_FONTSIZE = 12

COLOR_DESCRIPTION_CIRCLE_RADIUS = 5
# col=hex_to_rgb("#DCDBDB")

def create_header(pdf,patient,dates):
    # Name Tag
    pdf.setFillColorRGB(NAME_TAG_COLOR[0],NAME_TAG_COLOR[1],NAME_TAG_COLOR[2])
    pdf.roundRect(380,-1*NAME_TAG_RADIUS,width=NAME_TAG_WIDTH,height=NAME_TAG_HEIGHT+NAME_TAG_RADIUS,radius=NAME_TAG_RADIUS,fill=1,stroke=0)

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", NAME_TAG_FONTSIZE)
    pdf.drawString(420,4+NAME_TAG_FONTSIZE,"ID : "+str(patient['id']))
    pdf.drawString(420,23+NAME_TAG_FONTSIZE,"Name : "+patient['name'])
    pdf.drawString(420,43+NAME_TAG_FONTSIZE,"Contact : "+str(patient['contact']))

    pdf.line(0,NAME_TAG_HEIGHT,388,NAME_TAG_HEIGHT)

    # color discription
    pdf.setFillColorRGB(123/255,27/255,235/255)
    pdf.circle(27,74,COLOR_DESCRIPTION_CIRCLE_RADIUS,stroke=0,fill=1)
    pdf.setFillColorRGB(255/255,192/255,0)
    pdf.circle(141,74,COLOR_DESCRIPTION_CIRCLE_RADIUS,stroke=0,fill=1)
    pdf.setFillColorRGB(255/255,100/255,100/255)
    pdf.circle(179,74,COLOR_DESCRIPTION_CIRCLE_RADIUS,stroke=0,fill=1)
    pdf.setFillColorRGB(118/255,147/255,60/255)
    pdf.circle(217,74,COLOR_DESCRIPTION_CIRCLE_RADIUS,stroke=0,fill=1)
    pdf.setFillColorRGB(251/255,180/255,120/255)
    pdf.circle(269,74,COLOR_DESCRIPTION_CIRCLE_RADIUS,stroke=0,fill=1)
    pdf.setFillColorRGB(183/255,222/255,232/255)
    pdf.circle(414,74,COLOR_DESCRIPTION_CIRCLE_RADIUS,stroke=0,fill=1)
    pdf.setFillColorRGB(146/255,208/255,80/255)
    pdf.circle(478,74,COLOR_DESCRIPTION_CIRCLE_RADIUS,stroke=0,fill=1)

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(36,74+3,"DIFFERENT RANGE/UNIT")
    pdf.drawString(148,74+3,"LOW")
    pdf.drawString(186,74+3,"HIGH")
    pdf.drawString(223,74+3,"NORMAL")
    pdf.drawString(276,74+3,"IMPROVED,STILL OUT OF RANGE")
    pdf.drawString(421,74+3,"DECREASED")
    pdf.drawString(485,74+3,"IMPROVED")

    # Headings
    pdf.setFillColorRGB(196/255,196/255,196/255)
    pdf.roundRect(20,100,width=100,height=40,radius=5,stroke=0,fill=1)
    pdf.rect(20,100,width=20,height=20,stroke=0,fill=1)
    pdf.rect(20+100-20,100+40-20,width=20,height=20,stroke=0,fill=1)
    pdf.roundRect(123,100,width=100,height=40,radius=5,stroke=0,fill=1)
    pdf.rect(123,100,width=20,height=20,stroke=0,fill=1)
    pdf.rect(123+100-20,100+40-20,width=20,height=20,stroke=0,fill=1)
    pdf.roundRect(227,100,width=53,height=40,radius=5,stroke=0,fill=1)
    pdf.rect(227,100,width=20,height=20,stroke=0,fill=1)
    pdf.rect(227+53-20,100+40-20,width=20,height=20,stroke=0,fill=1)

    x=284
    for i in range(5):
        pdf.setFillColorRGB(250/255,241/255,241/255)
        pdf.roundRect(x,100,width=55,height=38,radius=5,stroke=0,fill=1)
        x+=343-284

    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(70,125,"LABEL")
    pdf.drawCentredString(173,125,"COMPARISON")
    pdf.drawCentredString(256,125,"DATE")

    x=284+55/2
    pdf.setFont("Helvetica", 12)
    for i in range(5):
        if(i<5-len(dates)):
            pdf.drawCentredString(x,125,"-")
        else:
            pdf.drawCentredString(x,125,dates[5-i-1][8:10]+"/"+dates[5-i-1][5:7]+"/"+dates[5-i-1][2:4])
        x+=343-284


def cal_lines(x):
    words=x.split()
    ca=16
    print_value = ""
    new_lines=1
    for word in words:
        if len(word)>ca:
            print_value = word
            ca=16-len(word)
            new_lines+=1
        else :
            ca-=len(word)
            print_value=print_value+ ("" if print_value=="" else " ") +word
        ca-=1
    return new_lines-1 if print_value=="" else new_lines

def write_comment(pdf,y,color):
    if(color.lower()=="#31b404" or color.lower()=="31b404"):
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//thumb.PNG",240,y+13,width=10,height=10)
        col = (6/255,62/255,1/255)
        pdf.setFillColorRGB(col[0],col[1],col[2])
        pdf.setFont("Helvetica",9)
        pdf.drawCentredString(200,y+34/2+5,"Normal, Looks good")
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//thumb.PNG",150,y+13,width=10,height=10)
    elif(color.lower()=="#ff0000" or color.lower()=="ff0000"):
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//angry.PNG",248,y+13,width=10,height=10)
        col = (82/255,4/255,4/255)
        pdf.setFillColorRGB(col[0],col[1],col[2])
        pdf.setFont("Helvetica",9)
        pdf.drawCentredString(200,y+34/2+5,"High, Need Some Work")
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//angry.PNG",142,y+13,width=10,height=10)
    elif(color.lower()=="#fe2e2e" or color.lower()=="fe2e2e"):
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//happy.PNG",251,y+13,width=11,height=10)
        col = (83/255,38/255,0)
        pdf.setFillColorRGB(col[0],col[1],col[2])
        pdf.setFont("Helvetica",9)
        pdf.drawCentredString(200,y+34/2+5,"Improved, Keep Working")
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//happy.PNG",139,y+13,width=11,height=10)
    elif(color.lower()=="#ffff00" or color.lower()=="ffff00"):
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//sad1.PNG",233,y+13,width=10,height=10)
        col = (98/255,78/255,18/255)
        pdf.setFillColorRGB(col[0],col[1],col[2])
        pdf.setFont("Helvetica",9)
        pdf.drawCentredString(200,y+34/2+5,"Low, Work Hard")
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//sad1.PNG",157,y+13,width=10,height=10)
    elif(color.lower()=="#82fa58" or color.lower()=="82fa58"):
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//clap.PNG",246,y+13,width=10,height=10)
        col = (44/255,65/255,21/255)
        pdf.setFillColorRGB(col[0],col[1],col[2])
        pdf.setFont("Helvetica",9)
        pdf.drawCentredString(200,y+34/2+5,"Improved, Keep Going")
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//clap.PNG",144,y+13,width=10,height=10)
    else:
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//sad.PNG",245,y+13,width=10,height=10)
        col = (78/255,96/255,101/255)
        pdf.setFillColorRGB(col[0],col[1],col[2])
        pdf.setFont("Helvetica",9)
        pdf.drawCentredString(200,y+34/2+5,"Decreases, Lets Work")
        pdf.drawImage(settings.MEDIA_ROOT.replace('/','//')+"//emojis//sad.PNG",144,y+13,width=10,height=10)



def run(data,user_id, patient):
    print("saved pdf at " +settings.MEDIA_ROOT)
    pdf = canvas.Canvas(settings.MEDIA_ROOT.replace('/','//')+"//Generated_reports//"+str(user_id)+".pdf",bottomup=0)
    # pdf = canvas.Canvas("latest.pdf",bottomup=0)
    x=20
    y=146+5
    # patient = {'id':11221133,'name':"prateek",'contact':124567890}
    data,dates=extract(data)
    create_header(pdf,patient,dates)

    for key in data:
        if(y+90>720):
            y=146+5
            pdf.line(0,FOOTER_START,595,FOOTER_START)
            pdf.showPage()
            create_header(pdf,patient,dates)
        # Label box
        pdf.setFillColorRGB(204/255,192/255,218/255)
        pdf.roundRect(x,y,width=253,height=18,radius=5,stroke=0,fill=1)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(x+253/2,y+12,key)
        y+=18+5

        for i in data[key]:
            if(y+80>720):
                y=146+5
                pdf.line(0,FOOTER_START,595,FOOTER_START)
                pdf.showPage()
                create_header(pdf,patient,dates)

            lines= cal_lines(i['label'])

            height= 57 if lines>1 else 38


            pdf.setFillColorRGB(247/255,238/255,238/255)
            pdf.roundRect(x,y,height=height,width=100,radius=5,stroke=0,fill=1)
            pdf.setFillColorRGB(22/255,22/255,22/255)
            pdf.setFont("Helvetica", 8)
            label_obj=Label.objects.filter(name=i['label'])[0]
            if lines==1:
                pdf.drawString(x+4,y+11+7,i['label'])
                pdf.setFont("Helvetica", 7)
                if(label_obj.upper_range):
                    pdf.drawString(x+4,y+11+13+7,"Range " +str(label_obj.lower_range)+"-"+str(label_obj.upper_range))
                else:
                    pdf.drawString(x+4,y+11+13+7,"Range Not Specified")
            else :
                words=i['label'].split()
                ca=16
                print_value = ""
                temp_y= 12 if lines==2 else 6
                new_lines=1
                for word in words:
                    if len(word)>ca:
                        pdf.drawString(x+4,y+temp_y+7+13*(new_lines-1),print_value)
                        print_value = word
                        ca=16-len(word)
                        new_lines+=1
                    else :
                        ca-=len(word)
                        print_value=print_value+ ("" if print_value=="" else " ") +word
                    ca-=1
                pdf.drawString(x+4,y+temp_y+7+13*(new_lines-1),print_value)
                if(lines==2):
                    pdf.setFont("Helvetica", 7)
                    if(label_obj.upper_range):
                        pdf.drawString(x+4,y+25+13+7,"Range " +str(label_obj.lower_range)+"-"+str(label_obj.upper_range))
                    else:
                        pdf.drawString(x+4,y+25+13+7,"Range Not Specified")

                else :
                    pdf.setFont("Helvetica", 7)
                    if(label_obj.upper_range): 
                        pdf.drawString(x+4,y+30+13+7,"Range " +str(label_obj.lower_range)+"-"+str(label_obj.upper_range))
                    else:
                        pdf.drawString(x+4,y+30+13+7,"Range Not Specified")

            # Comment box
            # print(i['color'][0])
            pdf.setFillColorRGB(i['color'][0][0],i['color'][0][1],i['color'][0][2])
            pdf.roundRect(124,y+(height/2)-34/2,width=150,height=34,radius=5,stroke=0,fill=1)
            write_comment(pdf,y+(height/2)-34/2,i['comment_color'])

            temp_x=284
            for iter in range(5):
                if(iter<5-len(dates)):
                    pdf.setFillColorRGB(183/255,222/255,232/255)
                else:
                    pdf.setFillColorRGB(i['color'][5-iter-1][0],i['color'][5-iter-1][1],i['color'][5-iter-1][2])
                pdf.roundRect(temp_x,y+(height/2)-38/2,width=55,height=38,radius=5,stroke=0,fill=1)
                pdf.setFillColorRGB(20/255,20/255,20/255)
                pdf.setFont("Helvetica", 14)
                if(iter<5-len(dates)):
                    pdf.drawCentredString(temp_x+55/2,y+(height/2)+5,"-")
                else:
                    pdf.drawCentredString(temp_x+55/2,y+(height/2)+5,str(i['values'][5-iter-1]) if str(i['values'][5-iter-1])!="" else "-")

                temp_x+=343-284
            y+=height+5

        y+=5

    pdf.save()

