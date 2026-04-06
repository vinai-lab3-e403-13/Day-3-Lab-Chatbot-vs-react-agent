# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Trịnh Ngọc Tú
- **Student ID**: 2A202600501
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: `tools/global_market_tool.py`, `tools/top_movers_tool.py`, `tools/trending_coins_tool.py`, `tools/search_crypto_tool.py`, `tools/historical_price_tool.py`, `tools/market_data_tool.py`
- **Code Highlights**:
def get_trending_coins() -> str:
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "coins" not in data:
            return json.dumps({"error": "No trending data found"})
            
        trending = []
        for item in data["coins"][:7]: # Limit to top 7
            coin = item["item"]
            trending.append({
                "id": coin.get("id"),
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "price_btc": coin.get("price_btc")
            })
            
        return json.dumps({"trending_coins": trending})
    except requests.RequestException as e:
        return json.dumps({"error": f"Failed to fetch trending coins from CoinGecko: {str(e)}"})

- **Documentation**: Các công cụ (tools) mới được lập trình (ví dụ: `get_trending_coins`) tương tác với vòng lặp ReAct thông qua 3 giai đoạn chính:
  **Khởi tạo và Cung cấp thông tin: Schema của tool được đăng ký trong file `__init__.py` và được inject vào `System Prompt` của LLM tại file `agent.py`. Do đó LLM biết được sự tồn tại và mục đích sử dụng của các công cụ này.
  **Ra quyết định: Khi người dùng đặt những câu hỏi liên quan, LLM sẽ phân tích (`Thought`) và quyết định gọi công cụ bằng cách xuất ra cú pháp chuẩn `Action: get_trending_coins({})`.
  **Thực thi & Thu thập kết quả: Bộ phân tách Regex của Agent sẽ trích xuất lệnh gọi này, chạy hàm Python tương ứng thông qua từ điển `execute_tool()`. Kết quả từ API được trả về dưới dạng chuỗi JSON và được đưa ngược lại cho LLM dưới vai trò là một `Observation`. Từ dữ liệu thực tế đó, LLM sẽ đóng gói và đưa ra câu trả lời cuối cùng (`Final Answer`).

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: when reach max_steps it return a simple text "Max steps reached" ignoring all the results before it.
- **Log Source**:
```json
{"timestamp": "2026-04-06T14:25:16.471167", "session_id": "32a314de", "event_type": "USER_INPUT", "user_input": "get eth price in 2026 jan 1 using historical price tool"}
{"timestamp": "2026-04-06T14:25:18.216381", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 1, "llm_raw_output": "The historical price tool can't predict future prices; it only provides past data. If you're interested in a future price scenario, we can discuss potential investment calculations or consult market experts for forecasts. Let me know if you'd like to explore those options!", "tokens": {"prompt_tokens": 849, "completion_tokens": 48, "total_tokens": 897}}
{"timestamp": "2026-04-06T14:25:20.006002", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 2, "llm_raw_output": "I'm unable to retrieve future prices with the historical price tool, as it only provides past data. If you need help with other types of price analysis or projections within the available datasets, please let me know!", "tokens": {"prompt_tokens": 849, "completion_tokens": 41, "total_tokens": 890}}
{"timestamp": "2026-04-06T14:25:22.027377", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 3, "llm_raw_output": "The get_historical_price tool can only retrieve past prices, not future ones. Therefore, I cannot provide the price of Ethereum for a future date like January 1, 2026. If you have any other questions or need assistance with a different tool, feel free to ask!", "tokens": {"prompt_tokens": 849, "completion_tokens": 57, "total_tokens": 906}}
{"timestamp": "2026-04-06T14:25:23.966815", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 4, "llm_raw_output": "The get_historical_price tool can only access historical data and cannot predict future prices. If you have any other type of request or need historical data, feel free to ask!", "tokens": {"prompt_tokens": 849, "completion_tokens": 35, "total_tokens": 884}}
{"timestamp": "2026-04-06T14:25:25.535672", "session_id": "32a314de", "event_type": "LLM_OUTPUT", "step": 5, "llm_raw_output": "The historical price tool can only retrieve past prices, not future predictions. Therefore, I can't provide a price for ETH on January 1, 2026. \n\nFor future price estimates, consider consulting price predictions from financial analysts or market forecasts. Let me know if you need something else!", "tokens": {"prompt_tokens": 849, "completion_tokens": 58, "total_tokens": 907}}
```
- **Diagnosis**: [Why did the LLM do this? Was it the prompt, the model, or the tool spec?]
- **Solution**: instead of return simple text error, try to get the latest result from **trace**

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: How did the `Thought` block help the agent compared to a direct Chatbot answer?
1. Khả năng lập kế hoạch và suy luận từng bước

Chatbot thường: Nhận câu hỏi và lập tức sinh ra câu trả lời cuối cùng ngay trong một nhịp. Điều này dễ dẫn đến hallucination nếu thông tin cần tính toán phức tạp.
ReAct Agent: Khối Thought đóng vai trò như một khoảng nghỉ trước khi quyết định thực thi Action.
2. Khả năng tự sửa lỗi

Chatbot thường: Nếu nó gọi nhầm dữ liệu hoặc thiếu thông tin, nó vẫn trả lời một cách tự tin nhưng sai lệch.
ReAct Agent: Khi Action thực thi xong và trả về Observation (có thể là một thông báo lỗi API do nhập sai ID mã token), Agent sẽ sinh ra vòng lặp Thought tiếp theo. Nhờ đó, Agent có thể tự thay đổi chiến thuật ngay trong phiên chat.
3. Tính minh bạch, dễ giám sát

Với một Chatbot thường, bạn chỉ nhận được mệnh lệnh "Đầu vào -> Đầu ra".
Với ReAct Agent, toàn bộ quá trình Thought được ghi lại vào log, giúp lập trình viên biết chính xác tại sao LLM lại đưa ra được kết quả đó, nó đã gọi những hàm nào, và sai ở bước tư duy nào để có thể tùy chỉnh lại Prompt.
2.  **Reliability**: In which cases did the Agent actually perform *worse* than the Chatbot?
Vì Agent phải lặp lại toàn bộ lịch sử hội thoại và các bước suy luận trung gian trong mỗi vòng lặp, số lượng token tiêu tốn sẽ tăng lên theo cấp số nhân. Với những câu hỏi mà chatbot có thể trả lời từ kiến thức nội tại, việc dùng Agent là một sự lãng phí tài nguyên lớn.
3.  **Observation**: How did the environment feedback (observations) influence the next steps?
**Cung cấp dữ liệu thực tế
**Điều hướng và sửa lỗi
**Khép kín vòng lặp suy luận
**Xác thực hành động
---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Sử dụng Message Queues như RabbitMQ, Kafka để xử lý các yêu cầu nặng hoặc các tool cần thời gian chờ lâu, giúp hệ thống không bị nghẽn khi có hàng ngàn người dùng cùng lúc.
- **Safety**: Thiết lập giới hạn số lần gọi API (quota) cho mỗi người dùng để tránh bị lạm dụng hoặc tấn công từ chối dịch vụ (DDoS), đồng thời kiểm soát chi phí LLM.
- **Performance**: Lưu lại các phản hồi hoặc kết quả từ Tool cho các câu hỏi phổ biến (ví dụ: "Giá BTC hiện tại") để trả về ngay lập tức mà không cần gọi lại LLM hay API bên thứ ba.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
