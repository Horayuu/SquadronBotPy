import datetime,re
DATE_PATTERN = re.compile(r"(\d{1,2}/\d{1,2}) ~ (\d{1,2}/\d{1,2})\s+(BR\s+\d{1,2}\.\d{1,1})")

def get_current_br():
  now = datetime.datetime.now()
  current_year = now.year
  try:
      with open("/home/py/DiscordBot_Server/br_cache") as f:
        cached_lines = f.readlines()
  except FileNotFoundError:
      raise FileNotFoundError("Cache File Not Found")
      #return "Cache File Not Found"

  for line in cached_lines:
    match = DATE_PATTERN.search(line)
    if match:
        start_date_str = match.group(1)
        end_date_str = match.group(2)
        br_value = match.group(3)
        try:
             start_dt = datetime.datetime.strptime(f"{current_year}/{start_date_str}", "%Y/%m/%d")
             end_dt = datetime.datetime.strptime(f"{current_year}/{end_date_str}", "%Y/%m/%d")
             end_dt = end_dt.replace(hour=22, minute=59, second=59)
             if start_dt <= now <= end_dt:
                    return br_value
        except ValueError as e:
             raise ValueError(f"Date Parsing Error: {e}")
             #return f"Date Parsing Error: {e}"
        except Exception as e:
             raise Exception(f"Unexpected Error: {e}")
             #return f"Unexpected Error: {e}"
  raise Exception("No Matching BR Found")

if __name__ == "__main__":
    current_br=get_current_br()
    print(current_br)