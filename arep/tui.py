from asciimatics.widgets import (
    Frame, ListBox, Layout, Divider, Text, CheckBox, Button, TextBox, Widget,
    RadioButtons, PopUpDialog
)
from asciimatics.exceptions import (
    ResizeScreenError, NextScene, StopApplication, InvalidFields
)
from asciimatics.scene import Scene
from asciimatics.screen import Screen
import argparse
import os
import sys

sys.path.append(os.path.dirname("/home/raf/Projects/Workspace/arep/"))
import arep


def argument_handler():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=str, help="path to the source, neo.")
    args = parser.parse_args()
    return args.source


class Grepper(object):
    def __init__(self, source):
        self.grepper = arep.Grepper(source)
        self.current_constraint = None

    def get_constraints(self):
        return self.grepper.constraint_list


class ListView(Frame):
    def __init__(self, screen, model):
        super(ListView, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            on_load=self._reload_list,
            hover_focus=True,
            title="Constraint List"
        )
        self._model = model
        self._button_names = ["Run", "Add", "Edit", "Delete", "Quit"]
        for name in self._button_names:
            setattr(
                self,
                "_{}_button".format(name.lower()),
                Button(name, getattr(self, "_{}".format(name.lower())))
            )

        self._list_view = ListBox(
            Widget.FILL_FRAME,
            model.grepper.constraint_list,
            name="constraints",
            on_change=self._on_pick
        )

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._list_view)
        layout.add_widget(Divider())

        layout2 = Layout([1] * len(self._button_names))
        self.add_layout(layout2)
        for name, position in zip(
                self._button_names, range(len(self._button_names))
        ):
            layout2.add_widget(
                getattr(self, "_{}_button".format(name.lower())),
                position
            )
        self.fix()
        self._on_pick()

    def _on_pick(self):
        self._edit_button.disabled = self._list_view.value is None
        self._delete_button.disabled = self._list_view.value is None

    def _reload_list(self):
        self._list_view.options = self._model.get_constraints()
        self._model.current_constraint = None

    def _add(self):
        self._model.current_constraint = None
        raise NextScene("Add constraint")

    def _edit(self):
        self.save()
        self._model.current_constraint = self.data["contacts"]
        raise NextScene("Edit Contact")

    def _delete(self):
        self.save()
        self._model.delete_contact(self.data["contacts"])
        self._reload_list()

    def _run(self):
        self.save()
        self._reload_list()

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")


class ConstraintTypes(Frame):
    def __init__(self, screen, model):
        super(ConstraintTypes, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            title="Add Constraint Type",
            reduce_cpu=True
        )
        self._model = model
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(
            RadioButtons(
                [(name, name) for name in ["Action", "Kind", "Properties"]],
                name="constraint_type",
            )
        )
        layout.add_widget(Divider(height=2))
        layout2 = Layout([1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Back", self._back), 1)
        layout2.add_widget(Button("Quit", self._quit), 2)
        self.fix()

    def reset(self):
        super(ConstraintTypes, self).reset()

    def _ok(self):
        self.save()
        if self.data['constraint_type'] == 'Action':
            raise NextScene("Add Action constraint")
        elif self.data['constraint_type'] == 'Kind':
            raise NextScene("Add Kind constraint")
        elif self.data['constraint_type'] == 'Properties':
            raise NextScene("Add Properties constraint")

    @staticmethod
    def _back():
        raise NextScene("Constraints")

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")


class Action(Frame):
    def __init__(self, screen, model):
        pass


class Kind(Frame):
    def __init__(self, screen, model):
        pass


class Properties(Frame):
    def __init__(self, screen, model):
        super(Properties, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            hover_focus=True,
            title="Add Properties constraint",
            reduce_cpu=True
        )
        self._model = model
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(
            RadioButtons(
                [(name, name) for name in ["Action", "Kind", "Properties"]],
                name="constraint_type",
            )
        )
        layout.add_widget(Divider(height=2))
        layout2 = Layout([1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("OK", self._ok), 0)
        layout2.add_widget(Button("Back", self._back), 1)
        layout2.add_widget(Button("Quit", self._quit), 2)
        self.fix()


class Results(Frame):
    def __init__(self, screen, model):
        pass


def Main():
    def app(screen, scene):
        scenes = [
            Scene([cls(screen, GrepperModel)], -1, name=name)
            for cls, name in [
                    (ListView, "Constraints"),
                    (ConstraintTypes, "Add constraint"),
                    (Action, "Add Action constraint"),
                    (Kind, "Add Kind constraint"),
                    (Properties, "Add Properties constraint"),
                    (Results, "Results")
            ]
        ]
        screen.play(scenes, stop_on_resize=True, start_scene=scene)

    source = argument_handler()
    GrepperModel = Grepper(source)
    last_scene = None
    while True:
        try:
            Screen.wrapper(app, catch_interrupt=True, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene


if __name__ == '__main__':
    Main()
