<style>
    .bordered {
        border: 1px solid black;
        padding: 10px;
        margin: 10px;
    }
</style>

<template>
<b>[{{ typeSymbols[type] }} {{ type }} filter]&nbsp;</b>
<label><input type="checkbox" v-model="_inverted" @change="emitDataChanged">🚫 Not</label>
&nbsp;

<!-- Tag Filter -->
<template v-if="type === 'tag'">
    <select v-model="_operation" @change="emitDataChanged">
        <option value="has">🫴 Has</option>
        <option value="has_only">🤏 Has Only</option>
    </select>
    <select v-model="_value" @change="emitDataChanged">
        <option v-for="tag in allTags" :value="tag">{{ tag }}</option>
    </select>
</template>

<!-- Color Filter -->
<template v-else-if="type === 'color'">
    <select v-model="_operation" @change="emitDataChanged">
        <option value="has">🫴 Has</option>
        <option value="has_only">🤏 Has Only</option>
    </select>
    <select v-model="_value" @change="emitDataChanged">
        <option v-for="color in allColors" :value="color">{{ color }}</option>
    </select>
</template>

<!-- Text Filter -->
<template v-else-if="type === 'text'">
    <select v-model="_columnName" @change="emitDataChanged">
        <option v-for="field in allTextFields" :value="field">{{ field }}</option>
    </select>
    <select v-model="_operation" @change="emitDataChanged">
        <option value="is">🟰 is</option>
        <option value="startswith">◀️ starts with</option>
        <option value="endswith">▶️ ends with</option>
        <option value="contains">🫙 contains</option>
    </select>
    <input v-model="_value" @change="emitDataChanged">
    &nbsp;
    <label><input type="checkbox" v-model="_caseSensitive" @change="emitDataChanged">🇦 Case Sensitive</label>
    &nbsp;
    <label><input type="checkbox" v-model="_showNull" @change="emitDataChanged">0️⃣ Show Null</label>
</template>

<!-- Number Filter -->
<template v-else-if="type === 'number'">
    <select v-model="_columnName" @change="emitDataChanged">
        <option v-for="field in allNumberFields" :value="field">{{ field }}</option>
    </select>
    <select v-model="_operation" @change="emitDataChanged">
        <option value="==">==</option>
        <option value="!=">!=</option>
        <option value="<">&lt;</option>
        <option value="<=">&lt;=</option>
        <option value=">">&gt;</option>
        <option value=">=">&gt;=</option>
    </select>
    <input v-model="_value" @change="emitDataChanged">
    &nbsp;
    <label><input type="checkbox" v-model="_showNull" @change="emitDataChanged">0️⃣ Show Null</label>

</template>

<!-- Boolean Filter -->
<template v-else-if="type === 'boolean'">
    <select v-model="_columnName" @change="emitDataChanged">
        <option v-for="field in allBooleanFields" :value="field">{{ field }}</option>
    </select>
    &nbsp;
    <label><input type="checkbox" v-model="_showNull" @change="emitDataChanged">0️⃣ Show Null</label>

</template>

<!-- Filter Group -->
<template v-else-if="type === 'group'">
    <div class="bordered">
    <template v-for="(filter, index) in _filters" :key="filter.uuid">
        <button @click="moveUp(index)" :disabled="index == 0">⬆️</button>
        <button @click="moveDown(index)" :disabled="index == _filters.length - 1">⬇️</button>
        <button @click="removeFilter(index)">🗑</button>
        &nbsp;
        <select v-if="index > 0" v-model="filter.operator">
            <option value="and">AND</option>
            <option value="or">OR</option>
        </select>
        &nbsp;
        <Filter
            :uuid="filter.uuid"
            :type="filter.type"
            :value="filter.value"
            :operation="filter.operation"
            :inverted="filter.inverted"
            :column-name="filter.columnName"
            :show-null="filter.showNull"
            :case-sensitive="filter.caseSensitive"
            :filters="filter.filters"
            :operator="filter.operator"
            @data-changed="filterDataChanged(index, $event)"
        ></Filter>
        <br>
    </template>
    <select v-model="newFilterType">
        <option value="text">🔤 Text</option>
        <option value="number">🔢 Number</option>
        <option value="boolean">🔘 Boolean</option>
        <option value="tag">🏷 Tag</option>
        <option value="color">🎨 Color</option>
        <option value="group">🗃 Group</option>
    </select>
    <button @click="addFilter()">➕ Add Filter</button>
    </div>
</template>
</template>

<script>
import axios from 'axios';

export default {
    name: 'Filter',
    emits: ['data-changed'],
    props: {
        uuid: String,
        type: String,
        value: String,
        operation: String,
        inverted: Boolean,
        columnName: String,
        showNull: Boolean,
        caseSensitive: Boolean,
        filters: Array,
        operator: String
    },
    data() {
        return {
            allTags: [],
            allColors: [],
            allTextFields: [],
            allNumberFields: [],
            allBooleanFields: [],

            _value: undefined,
            _operation: undefined,
            _inverted: undefined,
            _columnName: undefined,
            _showNull: undefined,
            _caseSensitive: undefined,
            _filters: undefined,
            _operator: undefined,

            newFilterType: "text",
            typeSymbols: {
                "text": "🔤",
                "number": "🔢",
                "boolean": "🔘",
                "tag": "🏷",
                "color": "🎨",
                "group": "🗃"
            }
        };
    },
    created() {
        this.getAllFields();
        this._value = this.value;
        this._operation = this.operation;
        this._inverted = this.inverted;
        this._columnName = this.columnName;
        this._show_null = this.showNull;
        this._caseSensitive = this.caseSensitive;
        this._filters = this.filters;
        this._operator = this.operator;
        this.emitDataChanged();

        this.emitter.on('newFilterData', (data) => {
            if (this.uuid != "root") {
                return;
            }
            this._value = data.value;
            this._operation = data.operation;
            this._inverted = data.inverted;
            this._columnName = data.columnName;
            this._show_null = data.showNull;
            this._caseSensitive = data.caseSensitive;
            this._filters = data.filters;
            this._operator = data.operator;
            this.emitDataChanged();
        });
    },
    methods: {
        getAllFields() {
            const basePath = "http://localhost:5000/";
            axios.get(basePath + "tags")
                .then((res) => {
                    this.allTags = res.data;
                })
                .catch((error) => {
                    console.error(error);
                });
            axios.get(basePath + "colors")
                .then((res) => {
                    this.allColors = res.data;
                })
                .catch((error) => {
                    console.error(error);
                });
            axios.get(basePath + "text-fields")
                .then((res) => {
                    this.allTextFields = res.data;
                })
                .catch((error) => {
                    console.error(error);
                });
            axios.get(basePath + "number-fields")
                .then((res) => {
                    this.allNumberFields = res.data;
                })
                .catch((error) => {
                    console.error(error);
                });
            axios.get(basePath + "boolean-fields")
                .then((res) => {
                    this.allBooleanFields = res.data;
                })
                .catch((error) => {
                    console.error(error);
                });
        },

        emitDataChanged() {
            this.$emit('data-changed', {
                "uuid": this.uuid,
                "type": this.type,
                "value": this._value,
                "operation": this._operation,
                "inverted": this._inverted,
                "columnName": this._columnName,
                "showNull": this._showNull,
                "caseSensitive": this._caseSensitive,
                "filters": this._filters,
                "operator": this._operator
            })
        },

        filterDataChanged(index, data) {
            this._filters[index] = data;
            this.emitDataChanged();
        },

        addFilter() {
            let newFilter;
            switch (this.newFilterType) {
                case "text":
                    newFilter = {
                        uuid: crypto.randomUUID(),
                        type: "text",
                        value: "",
                        operation: "contains",
                        inverted: false,
                        columnName: this.allTextFields[0],
                        showNull: false,
                        caseSensitive: false,
                        operator: "and"
                    };
                    break;
                case "number":
                    newFilter = {
                        uuid: crypto.randomUUID(),
                        type: "number",
                        value: 0,
                        operation: "==",
                        inverted: false,
                        columnName: this.allNumberFields[0],
                        showNull: false,
                        operator: "and"
                    };
                    break;
                case "boolean":
                    newFilter = {
                        uuid: crypto.randomUUID(),
                        type: "boolean",
                        inverted: false,
                        columnName: this.allBooleanFields[0],
                        showNull: false,
                        operator: "and"
                    };
                    break;
                case "tag":
                    newFilter = {
                        uuid: crypto.randomUUID(),
                        type: "tag",
                        value: this.allTags[0],
                        operation: "has",
                        inverted: false,
                        operator: "and"
                    };
                    break;
                case "color":
                    newFilter = {
                        uuid: crypto.randomUUID(),
                        type: "color",
                        value: this.allColors[0],
                        operation: "has",
                        inverted: false,
                        operator: "and"
                    };
                    break;
                case "group":
                    newFilter = {
                        uuid: crypto.randomUUID(),
                        type: "group",
                        filters: [],
                        operator: "and"
                    };
                    break;
            }
            this._filters.push(newFilter);
            this.emitDataChanged();
        },

        removeFilter(index) {
            this._filters.splice(index, 1);
            this.emitDataChanged();
        },

        swap(index1, index2) {
            [
                this._filters[index1],
                this._filters[index2]
            ] = [
                this._filters[index2],
                this._filters[index1]
            ];
            this.emitDataChanged();
        },

        moveUp(index) {
            this.swap(index, index - 1);
        },

        moveDown(index) {
            this.swap(index, index + 1);
        }


    },

};
</script>
