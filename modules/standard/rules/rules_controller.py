from core.command_param_types import Any, Const
from core.decorators import instance, command
from core.chat_blob import ChatBlob

@instance()
class RulesController:
    def __init__(self):
        pass

    def inject(self, registry):
        self.bot = registry.get_instance("bot")
        self.db: DB = registry.get_instance("db")

    def start(self):
        self.db.exec("CREATE TABLE IF NOT EXISTS rules (id INT PRIMARY KEY AUTO_INCREMENT, rule TEXT)")

    @command(command="rules",params=[], access_level="member", description="Show rules")
    def rules_cmd(self, request):
        rules_rows = self.get_rules()
        if rules_rows:
            return ChatBlob("Rules", self.format_rules_entries(self.get_news()))
        else:
            return ChatBlob("Rules", "No rules!\n\n LONG LIVE ANARCHY!")

    @command(command="rules_admin",params=[Const("add"),Any("rule")], access_level="admin", description="Add a new rule")
    def rules_admin_add_cmd(self, request, _, rule):
        sql = "INSERT INTO rules (rule) VALUES (?)"
        success = self.db.exec(sql, [rule])
        if success > 0:
            return "New rule with number <highlight>%d<end> added successfully." % self.db.last_insert_id()
        else:
            return "Failed to add news entry."

    def format_rules_entries(self, entries):
        blob = ""
        for item in entries:
            blob += "<highlight>%s)<end> %s\n" % (item.id, item.rule)
        return blob

    def get_rules(self):
        return self.db.query_single("SELECT * FROM rules ORDER BY id ASC")