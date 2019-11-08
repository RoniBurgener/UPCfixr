# This package allows servers, requests, urls, etc.
from flask import Flask, request, render_template, redirect, url_for
# Create app var from Flask package
app = Flask(__name__)

# This packages allows for saving files to app dir
import os
import pandas as pd
# Set path to upload csv (path of current app dirnae)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Create get route, function to run on request
@app.route('/')
def home_route():
    return render_template('upload.html')

# Create post route, function to run on request
@app.route('/results', methods=['POST', 'GET'])
def send_csv():
    if request.method == 'POST':
        if request.files['file'].filename == '' or request.files['file'].filename.endswith('.xlsx') == False:
            return redirect(url_for("home_route"))
        else:
            target = os.path.join(APP_ROOT, 'static/uploads')
            file = request.files['file']
            manid = request.form['manid']
            brandid = request.form['brandid']
            filename = file.filename
            destination = "/".join([target, filename])
            file.save(destination)
            df = pd.read_excel(destination,converters={'upc_given':str}) #reading client provided excel file
            df.columns = ['manufacturer_name','brand_name','sub_brand','product_category','product_sub_category','upc_given','product_description','quantity_pack_size','size','average_msrp','offer_id'] #labeling colummn names in data frame
            df['upc_given'] = df.upc_given.astype(str) #changes data type to strings
            df['offer_id'] = df.offer_id.astype(str) #changes data type to strings
            df['upc_given'] = df['upc_given'].str.replace('-','') #replacing all spaces and - and apostrophes with blanks
            df['upc_given'] = df['upc_given'].str.replace(' ','')
            df['upc_given'] = df['upc_given'].str.replace("'",'')

            def check_digit(data): #formula to calculate check digit from 11 digit long UPC string
                if (((int(data[0])+int(data[2])+int(data[4])+int(data[6])+int(data[8])+int(data[10]))*3 + (int(data[1])+int(data[3])+int(data[5])+int(data[7])+int(data[9])))%10) == 0:
                    return '0'
                else:
                    return str(10 - (((int(data[0])+int(data[2])+int(data[4])+int(data[6])+int(data[8])+int(data[10]))*3 + (int(data[1])+int(data[3])+int(data[5])+int(data[7])+int(data[9])))%10))

            def upcfxr10(UPC): #function assigns a "fix type" to a client provided UPC that is 10 digits long
                if check_digit('0'+'0'+ UPC[:-1]) == UPC[-1:]: #determines if adding two leading zero to the UPC produces the correct check digit
                    return "1"
                else:
                    return "2"

            def upcfxr10op1(UPC): #correctly formats 10 digit UPCs by adding two leading 0s
                UPC = '0'+'0'+ UPC
                return UPC
            def upcfxr10op2(UPC): #correctly formats 10 digit UPCs by adding one leading 0 and a check digit
                UPC11 = '0'+UPC
                UPC = '0'+UPC+check_digit(UPC11)
                return UPC

            def upcfxr11(UPC): #function assigns a "fix type" to a client provided UPC that is 11 digits long
                if check_digit('0'+ UPC[:-1]) == UPC[-1:]: #determines if adding one leading zero to the UPC produces the correct check digit
                    return "1"
                else:
                    return "2"

            def upcfxr11op1(UPC): #correctly formats 11 digit UPCs by adding one leading 0
                UPC = '0' + UPC
                return UPC
            def upcfxr11op2(UPC): #correctly formats 11 digit UPCs by adding a check digit
                UPC = UPC + check_digit(UPC)
                return str(UPC)

            def upcfxr12(UPC): #function assigns a "fix type" to a client provided UPC that is 12 digits long
                if check_digit(UPC[0:11]) == UPC[-1]: #determines if the check digit on the UPC is correct
                    return "1"
                elif UPC[0] == '0' and UPC[1] == '0': #determines if the UPC has two leading 0s
                    return "2"
                else:
                    return "3"

            def upcfxr12op1(UPC): #returns the client provided UPC without changes
                return UPC
            def upcfxr12op2(UPC): #drops one leading 0 from the UPC and adds a check digit
                UPC = UPC[1:12] + check_digit(UPC[1:12])
                return UPC
            def upcfxr12op3(UPC): #drops the check digit provided by the client and adds the correct one
                UPC = UPC[0:11] + check_digit(UPC[0:11])
                return UPC

            def upcfxr13(UPC): #function assigns a "fix type" to a client provided UPC that is 13 digits long
                if check_digit(UPC[1:12]) == UPC[-1] and UPC[0] == '0': #determines if the first leading zero is dropped, does the remaining 12 digit UPC have the correct check digit
                    return "1"
                elif UPC[0] == '0' and UPC[1] == '0': #determines if the client provided UPC has two leading zeros
                    return "2"
                else:
                    return "3"

            def upcfxr13op1(UPC): #drops the leading 0 from the UPC
                UPC = UPC[1:12]
                return UPC
            def upcfxr13op2(UPC): #drops both leading 0s and adds a check digit
                UPC = UPC[2:13] + check_digit(UPC[2:13])
                return UPC
            def upcfxr13op3(UPC): #drops the first leading 0 and replaces the last digit with the correct check digit
                UPC = UPC[1:12] + check_digit(UPC[1:12])
                return UPC

            def upcfxr14(UPC): #function assigns a "fix type" to a client provided UPC that is 14 digits long
                if check_digit(UPC[-11:]) == UPC[-1:] and UPC[0] == '0' and UPC[1] == '0': #determines if dropping the first two leading zero produces a UPC with a correct check digit
                    return "1"
                else:
                    return "2"

            def upcfxr14op1(UPC): #drops the first two leading 0s from the client provided UPC
                UPC = UPC[-12:]
                return UPC
            def upcfxr14op2(UPC): #drops the first three leading 0s from the client provided UPC and adds a check digit
                UPC = UPC[-11:] + check_digit(UPC[-11:])
                return UPC

            def lengthfinder (UPC): #returns the length of a UPC
                return int(len(UPC))

            df['upc_length'] = df['upc_given'].apply(lengthfinder) #creates a data frame with the length of the client provided UPCs
            upc_fix_type=[]

            #assigns a "fix type" for the UPC based on the length
            def upcfixtype(length, upc):
                if length == 14:
                    upc_fix_type.append(upcfxr14(upc))
                elif length == 13:
                    upc_fix_type.append(upcfxr13(upc))
                elif length == 12:
                    upc_fix_type.append(upcfxr12(upc))
                elif length == 11:
                    upc_fix_type.append(upcfxr11(upc))
                elif length == 10:
                    upc_fix_type.append(upcfxr10(upc))
                else:
                    print ('somethins jacked up')

            for index, row in df.iterrows():
                upcfixtype(row['upc_length'], row['upc_given'])

            #creates a data frame with the "fix types"
            df['upc_fix_type']=pd.DataFrame({'upc_fix_type':upc_fix_type})

            gk = df.groupby('upc_length')
            upc_fixed=[]

            #groups the client provided UPCs by length and applies the appropriate formatting function based on the mode of the fix type
            def upcfixer(y, x):
                print (y)
                if x == 14:
                    if int(gk.get_group(14).loc[:,'upc_fix_type'].mode()) == 1:
                        upc_fixed.append(upcfxr14op1(y))
                    else:
                        upc_fixed.append(upcfxr14op2(y))
                elif x == 13:
                    if int(gk.get_group(13).loc[:,'upc_fix_type'].mode()) == 1:
                        upc_fixed.append(upcfxr13op1(y))
                    elif int(gk.get_group(13).loc[:,'upc_fix_type'].mode()) == 2:
                        upc_fixed.append(upcfxr13op2(y))
                    else:
                        upc_fixed.append(upcfxr13op3(y))
                elif x == 12:
                    if int(gk.get_group(12).loc[:,'upc_fix_type'].mode()) == 1:
                        upc_fixed.append(upcfxr12op1(y))
                    elif int(gk.get_group(12).loc[:,'upc_fix_type'].mode()) == 2:
                        upc_fixed.append(upcfxr12op2(y))
                    else:
                        upc_fixed.append(upcfxr12op3(y))
                elif x == 11:
                    if int(gk.get_group(11).loc[:,'upc_fix_type'].mode()) == 1:
                        upc_fixed.append(upcfxr11op1(y))
                    else:
                        upc_fixed.append(upcfxr11op2(y))
                elif x == 10:
                    if int(gk.get_group(10).loc[:,'upc_fix_type'].mode()) == 1:
                        upc_fixed.append(upcfxr10op1(y))
                    else:
                        upc_fixed.append(upcfxr10op2(y))
                else: #labels all UPCs that are not 10 to 14 digits to be deleted
                    upc_fixed.append('gerd dammit')

            for index, row in df.iterrows():
                upcfixer(row['upc_given'], row['upc_length'])

            #creates a data frame with the correctly formatted UPCs
            df['upc_fixed']=pd.DataFrame({'upc_fixed':upc_fixed})

            #for loop to QC UPCs
            upc_fixed_final=[]

            def qc_check(UPC):
                if UPC == 'gerd dammit':
                    upc_fixed_final.append(UPC)
                elif check_digit(UPC[0:11]) == UPC[-1]:
                    upc_fixed_final.append(UPC)
                else:
                    upc_fixed_final.append(UPC[0:11] + check_digit(UPC[0:11]))

            for index, row in df.iterrows():
                qc_check(row['upc_fixed'])

            df['upc_fixed_final']=pd.DataFrame({'upc_fixed_final':upc_fixed_final})

            #assigning data frames to columns in CSV to be uploaded to admin
            csvfinal = pd.DataFrame(columns = ['Offer ID','Manufacturer ID','Brand ID','Product Size','SIZE UOM','offer product group id','UPC','Product Description','Costco Code','Target DPCI','Sams Item Code','Generate Check Digit'])
            csvfinal['UPC'].to_string()

            csvfinal['UPC'] = df['upc_fixed_final']
            csvfinal['Manufacturer ID'] = manid
            csvfinal['Brand ID'] = brandid
            csvfinal['Product Size'] = '1'
            csvfinal['SIZE UOM'] = 'ct'
            csvfinal['Offer ID'] = df['offer_id']
            csvfinal['Product Description'] = df['product_description']
            csvfinal[['offer product group id','Costco Code','Target DPCI','Sams Item Code','Generate Check Digit']]=""

            csvfinal = csvfinal[csvfinal.UPC != 'gerd dammit']
            os.remove(destination)

            csvfinal.to_csv(target + '/UPCstoUploadtoAdmin.csv')

            return render_template('results.html')
    else:
            return redirect(url_for("home_route"))

# This runs the server (provided by Flask)
if __name__ == '__main__':
    app.run(debug=True)
