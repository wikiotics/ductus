# Ductus
# Copyright (C) 2011  Jim Garrison <garrison@wikiotics.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ductus.modules.flashcards import registered_interaction_views

def register_interaction_view(model):
    def _register_interaction_view(func):
        if model.fqn in registered_interaction_views:
            raise Exception("An interaction view is already registered for: %s"
                            % model.fqn)
        registered_interaction_views[model.fqn] = func
        return func
    return _register_interaction_view
