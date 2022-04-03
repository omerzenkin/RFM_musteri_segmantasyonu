#Gerekli kütüphanelerin indirilmesini yapıyoruz
import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
df_ = pd.read_csv("dataa/RFM_data_20k.csv")
df = df_.copy()

#Veri setini anlamaya çalışıyoruz
df.head(10)
df.columns
df.describe().T
df.isnull().sum()
df.info()

# Herbir müşterinin toplam alışveriş sayısı ve harcaması için yeni değişkenler oluşturunuz
df["total_order"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]

df["total_value"] = df["customer_value_total_ever_offline"] + df["customer_value_total_ever_online"]

#Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriyoruz.

date_columns = df.columns[df.columns.str.contains("date")]
df[date_columns] = df[date_columns].apply(pd.to_datetime)
df.info()

#analiz tarihi oluşturup recency, frequnecy ve monetary değerlerinin yer aldığı yeni bir rfm dataframe oluşturuyoruz
df["last_order_date"].max() # 2021-05-30
analysis_date = dt.datetime(2021,6,1)

rfm = pd.DataFrame()
rfm["customer_id"] = df["master_id"]
rfm["recency"] = (analysis_date - df["last_order_date"]).astype('timedelta64[D]')
rfm["frequency"] = df["order_num_total"]
rfm["monetary"] = df["customer_value_total"]


#Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çevrilmesi ve
#Bu skorları recency_score, frequency_score ve monetary_score olarak kaydedilmesini sağlıyoruz

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str))

#regex ile segmentlere ayırıyoruz

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

#segmentlerin ortalamalarını inceliyoruz
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

