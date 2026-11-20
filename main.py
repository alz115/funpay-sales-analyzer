import glob
import os
import pandas as pd


print(r"""
  _____ _   _ _   _ ____   _ __   __   ____    _    _     _____ ____  
 |  ___| | | | \ | |  _ \ / \\ \ / /  / ___|  / \  | |   | ____/ ___| 
 | |_  | | | |  \| | |_) / _ \\ V /   \___ \ / _ \ | |   |  _| \___ \ 
 |  _| | |_| | |\  |  __/ ___ \| |     ___) / ___ \| |___| |___ ___) |
 |_| _  \___/|_| \_|_| /_/ __\_\_|    |____/_/___\_\_____|_____|____/ 
    / \  | \ | |  / \  | | \ \ / /__  / ____|  _ \                   
   / _ \ |  \| | / _ \ | |  \ V /  / /|  _| | |_) |                  
  / ___ \| |\  |/ ___ \| |___| |  / /_| |___|  _ <                   
 /_/   \_\_| \_/_/   \_\_____|_| /____|_____|_| \_\                  
""")
folder_path = '.'
search_pattern = os.path.join(folder_path, 'funpay_sales_*')

# initialization and loading
files = glob.glob(search_pattern)
only_files = [f for f in files if os.path.isfile(f)]

if only_files:
    files_sorted = sorted(only_files, key=os.path.getmtime, reverse=True)
    latest_file = files_sorted[0]
    print(f"Загружаю самый свежий файл: {latest_file}")

    df = pd.read_csv(latest_file)
    df["amount"] = df["amount"].astype(float)

    # успешные заказы — считаем один раз
    ok = df[(df["status"].isin(["paid", "closed"])) & df["refunded_at"].isna()].copy()

else:
    print("По шаблону найдены только папки, файлов нет.")
    df = None
    ok = None


# number of orders
def count_orders():
    print("\nКоличество заказов:")
    print("  всего — 1")
    print("  по играм — 2")
    print("  по разделам — 3")
    print("  по продавцам — 4")
    print("  по покупателям — 5")
    print("  по статусам — 6")
    print("  по валютам — 7")
    r = input("Введите число: ")
    if r == "1":
        print(f"Всего: {len(ok)}")
    elif r == "2":
        print(ok["game_name"].value_counts())
    elif r == "3":
        print(ok["section_name"].value_counts())
    elif r == "4":
        print(ok["seller_name"].value_counts())
    elif r == "5":
        print(ok["buyer_name"].value_counts())
    elif r == "6":
        print(df["status"].value_counts())
    elif r == "7":
        print(ok["currency"].value_counts())
    else:
        print("Нет такого варианта")


#GMV (revenue)
def gmv():
    print("\nGMV:")
    print("  общий — 1")
    print("  по играм — 2")
    print("  по разделам — 3")
    print("  по продавцам — 4")
    print("  по валютам — 5")
    print("  по дням — 6")
    r = input("Введите число: ")
    if r == "1":
        print(ok.groupby("currency")["amount"].sum())
    elif r == "2":
        print(ok.groupby(["game_name", "currency"])["amount"].sum().sort_values(ascending=False))
    elif r == "3":
        print(ok.groupby(["section_name", "currency"])["amount"].sum().sort_values(ascending=False))
    elif r == "4":
        print(ok.groupby(["seller_name", "currency"])["amount"].sum().sort_values(ascending=False))
    elif r == "5":
        print(ok.groupby("currency")["amount"].sum())
    elif r == "6":
        d = ok.copy()
        d["date"] = pd.to_datetime(d["paid_at"]).dt.date
        print(d.groupby(["date", "currency"])["amount"].sum())
    else:
        print("Нет такого варианта")


# AOV (average order value)
def aov():
    print("\nAOV (средний чек):")
    print("  общий — 1")
    print("  по играм — 2")
    print("  по разделам — 3")
    print("  по продавцам — 4")
    print("  по валютам — 5")
    r = input("Введите число: ")
    if r == "1":
        print((ok.groupby("currency")["amount"].sum()
               / ok.groupby("currency")["order_uid"].count()).round(2))
    elif r == "2":
        print(ok.groupby(["game_name", "currency"])["amount"].mean().round(2).sort_values(ascending=False))
    elif r == "3":
        print(ok.groupby(["section_name", "currency"])["amount"].mean().round(2).sort_values(ascending=False))
    elif r == "4":
        print(ok.groupby(["seller_name", "currency"])["amount"].mean().round(2).sort_values(ascending=False))
    elif r == "5":
        print(ok.groupby("currency")["amount"].mean().round(2))
    else:
        print("Нет такого варианта")


# returns and cancellations
def refunds():
    total = len(df)
    full = df["refunded_at"].notna().sum()
    partial = df["partially_refunded_at"].notna().sum()
    print("\nВозвраты:")
    print(f"  всего заказов: {total}")
    print(f"  полных возвратов: {full} ({full/total*100:.1f}%)")
    print(f"  частичных возвратов: {partial} ({partial/total*100:.1f}%)")
    print("\nПо статусам:")
    print(df["status"].value_counts())
    print("\nПо играм (полные возвраты):")
    print(df[df["refunded_at"].notna()]["game_name"].value_counts())
    print("\nПо продавцам (полные возвраты):")
    print(df[df["refunded_at"].notna()]["seller_name"].value_counts())


# 5. funnel: created → paid → closed
def funnel():
    created = len(df)
    paid = df["paid_at"].notna().sum()
    closed = df["closed_at"].notna().sum()
    print("\nВоронка заказов:")
    print(f"  создано:  {created}")
    print(f"  оплачено: {paid} ({paid/created*100:.1f}%)")
    print(f"  закрыто:  {closed} ({closed/created*100:.1f}%)")

    # время до оплаты / до закрытия
    d = df.copy()
    d["paid_at"] = pd.to_datetime(d["paid_at"], errors="coerce")
    d["created_at"] = pd.to_datetime(d["created_at"], errors="coerce")
    d["closed_at"] = pd.to_datetime(d["closed_at"], errors="coerce")

    to_paid = (d["paid_at"] - d["created_at"]).dt.total_seconds() / 60
    to_closed = (d["closed_at"] - d["paid_at"]).dt.total_seconds() / 60

    print(f"\nВремя до оплаты (мин): медиана {to_paid.median():.1f}, среднее {to_paid.mean():.1f}")
    print(f"Время до закрытия (мин): медиана {to_closed.median():.1f}, среднее {to_closed.mean():.1f}")


# reviews and rating
def reviews():
    d = ok[ok["review_rating"].notna()].copy()
    d["review_rating"] = pd.to_numeric(d["review_rating"], errors="coerce")
    print(f"\nОтзывов: {len(d)} из {len(ok)} заказов ({len(d)/len(ok)*100:.1f}%)")
    print(f"Средний рейтинг: {d['review_rating'].mean():.2f}")
    print("\nРаспределение оценок:")
    print(d["review_rating"].value_counts().sort_index())
    print("\nСредний рейтинг по продавцам:")
    print(d.groupby("seller_name")["review_rating"].agg(["mean", "count"]).round(2).sort_values("mean", ascending=False))
    print("\nСредний рейтинг по играм:")
    print(d.groupby("game_name")["review_rating"].agg(["mean", "count"]).round(2).sort_values("mean", ascending=False))
    print("\nДоля отзывов с ответом продавца:")
    answered = d["review_reply"].notna().sum()
    print(f"  {answered} ({answered/len(d)*100:.1f}%)")



# buyers

def buyers():
    print(f"\nУникальных покупателей: {ok['buyer_user_id'].nunique()}")
    freq = ok.groupby("buyer_user_id").size()
    print(f"Покупателей с 1 заказом: {(freq == 1).sum()}")
    print(f"Покупателей с 2+ заказами: {(freq >= 2).sum()} ({(freq >= 2).sum()/len(freq)*100:.1f}%)")
    print("\nТоп-10 покупателей по числу заказов:")
    print(ok.groupby("buyer_name").size().sort_values(ascending=False).head(10))
    print("\nТоп-10 покупателей по сумме (по валютам):")
    print(ok.groupby(["buyer_name", "currency"])["amount"].sum().sort_values(ascending=False).head(10))

# games and sections
def games():
    print("\nПо играм (заказы / выручка / AOV):")
    g = ok.groupby(["game_name", "currency"]).agg(
        orders=("order_uid", "count"), revenue=("amount", "sum"), aov=("amount", "mean"), ).round(2).sort_values("revenue", ascending=False)
    print(g)
    print("\nПо разделам (заказы / выручка / AOV):")
    s = ok.groupby(["section_name", "currency"]).agg(
        orders=("order_uid", "count"),
        revenue=("amount", "sum"),
        aov=("amount", "mean"), ).round(2).sort_values("revenue", ascending=False)
    print(s)


# dynamics by day
def daily():
    d = ok.copy()
    d["paid_at"] = pd.to_datetime(d["paid_at"], errors="coerce")
    d["date"] = d["paid_at"].dt.date
    g = d.groupby(["date", "currency"]).agg(
        orders=("order_uid", "count"),
        revenue=("amount", "sum"),
        aov=("amount", "mean"),
    ).round(2)
    print("\nДинамика по дням:")
    print(g)

# auto-delivery and manual
def delivery():
    import json
    d = ok.copy()
    def is_auto(x):
        try:
            return json.loads(x).get("auto_delivery", False)
        except Exception:
            return False
    d["auto"] = d["type_data"].apply(is_auto)
    print("\nАвто-доставка vs ручная:")
    print(d.groupby(["auto", "currency"]).agg(
        orders=("order_uid", "count"),
        revenue=("amount", "sum"),
        aov=("amount", "mean"),
    ).round(2))
    print(f"\nДоля авто-доставки: {d['auto'].sum()}/{len(d)} ({d['auto'].mean()*100:.1f}%)")



# servers and parties
def servers():
    d = ok[ok["server_name"].notna()]
    if len(d) == 0:
        print("\nНет данных по серверам.")
        return
    print("\nПо серверам:")
    print(d.groupby(["server_name", "currency"]).agg(
        orders=("order_uid", "count"),
        revenue=("amount", "sum"),
    ).round(2).sort_values("orders", ascending=False))
    d2 = ok[ok["side_name"].notna()]
    if len(d2):
        print("\nПо сторонам:")
        print(d2.groupby(["side_name", "currency"]).agg(
            orders=("order_uid", "count"),
            revenue=("amount", "sum"),
        ).round(2).sort_values("orders", ascending=False))


def main():
    if ok is None:
        return
    while True:
        print("\nMENU")
        print("  1 — Количество заказов")
        print("  2 — GMV (выручка)")
        print("  3 — AOV (средний чек)")
        print("  4 — Возвраты и отмены")
        print("  5 — Воронка и время обработки")
        print("  6 — Отзывы и рейтинг")
        print("  7 — Покупатели")
        print("  8 — Игры и разделы")
        print(" 9 — Динамика по дням")
        print(" 10 — Авто-доставка и ручная")
        print(" 11 — Серверы / стороны")
        print("  0 — Выход")
        choice = input("Введите число: ")
        if choice == "1":   count_orders()
        elif choice == "2": gmv()
        elif choice == "3": aov()
        elif choice == "4": refunds()
        elif choice == "5": funnel()
        elif choice == "6": reviews()
        elif choice == "7": buyers()
        elif choice == "8": games()
        elif choice == "9": daily()
        elif choice == "10": delivery()
        elif choice == "11": servers()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Нет такого варианта")


if __name__ == "__main__":
    main()