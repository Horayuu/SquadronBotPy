import datetime,re

now = datetime.datetime.now()
with open("/home/py/DiscordBot_Server/br_cache") as f:
        cached_lines = f.readlines()


#lines = cached_lines.strip().split('\n')
DATE_PATTERN = re.compile(r"(\d{1,2}/\d{1,2}) ~ (\d{1,2}/\d{1,2})\s+(BR\s+\d{1,2}\.\d{1,1})")
current_year = now.year
def get_current_br():
  for line in cached_lines:
    match = DATE_PATTERN.search(line)
    if match:
        start_date_str = match.group(1)
        end_date_str = match.group(2)
        br_value = match.group(3)
        try:
             start_dt = datetime.datetime.strptime(f"{current_year}/{start_date_str}", "%Y/%m/%d")
             end_dt = datetime.datetime.strptime(f"{current_year}/{end_date_str}", "%Y/%m/%d")
             end_dt = end_dt.replace(hour=23, minute=59, second=59)
             if start_dt <= now <= end_dt:
                    return br_value
        except ValueError as e:
             return f"Date Parsing Error: {e}"

if __name__ == "__main__":
    current_br=get_current_br()
    print(current_br)