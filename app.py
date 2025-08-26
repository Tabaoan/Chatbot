from chains import make_chatbot
from router import core_chain

def main():
    session = "demo"
    chatbot = make_chatbot(core_chain)

    print("Chatbot 3 nhánh (Tavily + PDF + General) có lịch sử. Gõ 'exit' để thoát, 'clear' để xóa lịch sử.")
    while True:
        msg = input("> Bạn: ").strip()
        if msg.lower() in {"exit", "quit"}: break
        if msg.lower() == "clear":
            from .chains import store
            if session in store:
                store[session].clear()
                print("✅ Đã xóa lịch sử.\n")
            continue
        try:
            resp = chatbot.invoke({"message": msg}, config={"configurable": {"session_id": session}})
            print("\nBot:", resp, "\n")
        except Exception as e:
            print(f"❌ Lỗi: {e}\n")

if __name__ == "__main__":
    main()
