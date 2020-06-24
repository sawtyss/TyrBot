from core.command_param_types import Any, Const, Int
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
        rules_intro = self.get_rules_intro()
        rules_blob = "No rules!\n\n<highlight>LONG LIVE ANARCHY!<end>"
        if rules_rows:
            rules_blob = self.format_rules_entries(rules_intro, rules_rows)
        return ChatBlob("Rules", rules_blob)

    @command(command="rules",params=[Const("intro"), Const("set"), Any("intro")], access_level="admin", description="Set the preamble section of rules", sub_command="update")
    def rules_intro_cmd(self, request, _, __, intro):
        success = self.update_rule_in_db(-1, intro)
        if success > 0:
            return "Rules introduction set successfully."
        else:
            return "Failed to set rules introduction."

    @command(command="rules",params=[Const("intro"),Const("delete")], access_level="admin", description="Delete the preamble section of rules", sub_command="update")
    def rules_delete_intro_cmd(self, request, _, __):
        success = self.delete_rule_from_db(-1)
        if success > 0:
            return "Rules introduction deleted successfully."
        else:
            return "Failed to delete rules introduction."

    @command(command="rules",params=[Const("set"),Int("rule_id"), Any("rule")], access_level="admin", description="Create/update a rule", sub_command="update")
    def rules_set_cmd(self, request, _, rule_id, rule):
        success = self.update_rule_in_db(rule_id, rule)
        if success > 0:
            return "Rule number <highlight>%d<end> updated successfully." % rule_id
        else:
            return "Failed to update rule number <highlight>%d<end>." % rule_id

    @command(command="rules",params=[Const("delete"),Int("rule_id")], access_level="admin", description="Delete an existing rule", sub_command="update")
    def rules_delete_cmd(self, request, _, rule_id):
        sql = "DELETE FROM rules where id = ?"
        success = self.db.exec(sql, [rule_id])
        if success > 0:
            return "Rule number <highlight>%d<end> deleted successfully." % rule_id
        else:
            return "Failed to delete rule number <highlight>%d<end>." % rule_id

    def delete_rule_from_db(self, rule_id):
        sql = "DELETE FROM rules where id = ?"
        return self.db.exec(sql, [rule_id])

    def update_rule_in_db(self, rule_id, rule):
        sql = "UPDATE rules set rule = ? where id = ?"
        success = self.db.exec(sql, [rule, rule_id])
        if not success > 0:
            sql = "INSERT INTO rules (id, rule) VALUES (?,?)"
            success = self.db.exec(sql, [rule_id, rule])
        return success

    def format_rules_entries(self, introduction, entries):
        blob = ""
        nr = 1
        if introduction:
            blob += "<highlight>%s<end>\n\n" % introduction
        for item in entries:
            blob += "<highlight>%s)<end> <font color='yellow'>%s</font>\n" % (item.id, item.rule)
            nr += 1
        return blob

    def get_rules(self):
        return self.db.query("SELECT * FROM rules WHERE id > 0 ORDER BY id ASC")

    def get_rules_intro(self):
        return self.db.query_single("SELECT rule FROM rules WHERE id = -1").rule